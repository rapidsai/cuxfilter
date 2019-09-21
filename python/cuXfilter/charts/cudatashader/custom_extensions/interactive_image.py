from __future__ import absolute_import

from distutils.version import LooseVersion

import bokeh
import uuid


from bokeh.document import Document
from bokeh.models import ColumnDataSource

bokeh_version = LooseVersion(bokeh.__version__)

if bokeh_version > '0.12.9':
    from bokeh.embed.notebook import encode_utf8, notebook_content
else:
    from bokeh.embed import notebook_div

import time

NOTEBOOK_DIV = """
{plot_div}
<script type="text/javascript">
  {plot_script}
</script>
"""

def bokeh_notebook_div(image):
    """"
    Generates an HTML div to embed in the notebook.

    Parameters
    ----------
    image: InteractiveImage
        InteractiveImage instance with a plot

    Returns
    -------
    div: str
        HTML string containing the bokeh plot to be displayed
    """
    if bokeh_version > '0.12.9':
        js, div, _ = notebook_content(image.p, image.ref)
        html = NOTEBOOK_DIV.format(plot_script=js, plot_div=div)
        div = encode_utf8(html)
        # Ensure events are held until an update is triggered
        image.doc.hold()
    else:
        div = notebook_div(image.p, image.ref)
    return div


class InteractiveImage(object):
    """
    Bokeh-based interactive image object that updates on pan/zoom
    events.

    Given a Bokeh plot and a callback function, calls the function
    whenever the pan or zoom changes the plot's extent, regenerating
    the image dynamically.

    Parameters
    ----------
    bokeh_plot : plot or figure
        Bokeh plot the image will be drawn on
    callback : function
        Python callback function with the signature::

           fn(x_range=(xmin, xmax), y_range=(ymin, ymax),
              w, h, **kwargs)

        and returning a PIL image object.
    timeout: int
        Determines the timeout after which the callback will
        process new events without the previous one having
        reported completion. Increase for very long running
        callbacks.
    **kwargs
        Any kwargs provided here will be passed to the callback
        function.
    """
    def callback_py(self, attr, old, new):
        now = time.time()
        if now - self.last_run < self.timeout:
            pass
        else:
            self.last_run = time.time()
            # time.sleep(self.timeout)
            self.update_chart()

    def update_chart(self, **kwargs):
        dict_temp = {
            'xmin': self.p.x_range.start,
            'ymin': self.p.y_range.start,
            'xmax': self.p.x_range.end,
            'ymax': self.p.y_range.end,
            'w': self.p.plot_width,
            'h': self.p.plot_height
            }
        self.kwargs.update(kwargs)
        self.update_image(dict_temp)

    _callbacks = {}

    def __init__(self, bokeh_plot, callback, delay=200, timeout=0.2, **kwargs):
        self.p = bokeh_plot
        self.callback = callback
        self.kwargs = kwargs
        self.ref = str(uuid.uuid4())

        self.timeout = timeout

        # Initialize the image and callback
        self.ds, self.renderer = self._init_image()
        self.last_run = time.time()
        self.p.x_range.on_change('start', self.callback_py)
        self.p.y_range.on_change('start', self.callback_py)


    def _init_image(self):
        """
        Initialize RGBA image glyph and datasource
        """
        width, height = self.p.plot_width, self.p.plot_height
        xmin, xmax = self.p.x_range.start, self.p.x_range.end
        ymin, ymax = self.p.y_range.start, self.p.y_range.end

        x_range = (xmin, xmax)
        y_range = (ymin, ymax)
        dw, dh = xmax - xmin, ymax - ymin
        image = self.callback(x_range, y_range, width, height, **self.kwargs)

        ds = ColumnDataSource(data=dict(image=[image.data], x=[xmin],
                                        y=[ymin], dw=[dw], dh=[dh]))
        renderer = self.p.image_rgba(source=ds, image='image', x='x', y='y',
                                     dw='dw', dh='dh', dilate=False)
        return ds, renderer

    def update_image(self, ranges):
        """
        Updates image with data returned by callback
        """
        x_range = (ranges['xmin'], ranges['xmax'])
        y_range = (ranges['ymin'], ranges['ymax'])
        dh = (y_range[1] - y_range[0])
        dw = (x_range[1] - x_range[0])

        image = self.callback(x_range, y_range, ranges['w'],
                              ranges['h'], **self.kwargs)
        new_data = dict(image=[image.data], x=[x_range[0]],
                        y=[y_range[0]], dw=[dw], dh=[dh])
        
        self.ds.data.update(new_data)

    def _repr_html_(self):
        self.doc = Document()
        for m in self.p.references():
            m._document = None
        self.doc.add_root(self.p)
        return bokeh_notebook_div(self)
