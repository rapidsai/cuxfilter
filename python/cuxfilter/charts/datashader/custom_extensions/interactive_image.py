from __future__ import absolute_import

from packaging.version import Version
import bokeh
from bokeh.document import Document
from bokeh.models import ColumnDataSource, CustomJS, Slider
import uuid

bokeh_version = Version(bokeh.__version__)

if bokeh_version > Version("0.12.9"):
    from bokeh.embed.notebook import notebook_content
else:
    from bokeh.embed import notebook_div

NOTEBOOK_DIV = """
{plot_div}
<script type="text/javascript">
  {plot_script}
</script>
"""


def bokeh_notebook_div(image):
    """
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
    if bokeh_version > "0.12.9":
        js, div, _ = notebook_content(image.p, image.ref)
        div = NOTEBOOK_DIV.format(plot_script=js, plot_div=div)
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
    timeout: int (milliseconds), default 100
        Determines the timeout after which the callback will
        process new events without the previous one having
        reported completion. Increase for very long running
        callbacks.
    **kwargs
        Any kwargs provided here will be passed to the callback
        function.
    """

    def callback_js(self):
        js_code = """

            //debouncing

            function update_plot() {
                if(Bokeh._queued.length){
                    if (hidden_chart.value == 0){
                        hidden_chart.value = 1
                    }else{
                        hidden_chart.value = 0
                    }
                    Bokeh._timeout = Date.now();
                    Bokeh._queued = [];
                }
            }

            window.addEventListener('resize', update_plot);


            if (!Bokeh._queued) {{
                Bokeh._queued = [];
                //so that first callback is executed
                Bokeh._timeout = Date.now() - __timeout;
            }}

            if((Date.now() - Bokeh._timeout) < __timeout){
                Bokeh._queued = [cb_obj]
            }else{
                Bokeh._queued = [cb_obj];
                update_plot()
                setTimeout(update_plot, __timeout)
            }

        """
        return CustomJS(
            args=dict(
                hidden_chart=self.hidden_chart,
                __timeout=self.timeout,
            ),
            code=js_code,
        )

    def callback_py(self, attr, old, new):
        self.update_chart()

    def update_chart(self, **kwargs):
        dict_temp = {
            "xmin": self.p.x_range.start,
            "ymin": self.p.y_range.start,
            "xmax": self.p.x_range.end,
            "ymax": self.p.y_range.end,
            "w": self.p.plot_width,
            "h": self.p.plot_height,
        }
        self.kwargs.update(kwargs)
        self.update_image(dict_temp)

    _callbacks = {}

    def __init__(
        self, bokeh_plot, callback, delay=200, timeout=10000, **kwargs
    ):
        self.p = bokeh_plot
        self.callback = callback
        self.kwargs = kwargs
        self.ref = str(uuid.uuid4())
        self.timeout = timeout
        self.hidden_chart = Slider(visible=False, start=0, end=1, value=0)
        # Initialize the image and callback
        self.ds, self.renderer = self._init_image()
        self.p.x_range.js_on_change("start", self.callback_js())
        self.p.y_range.js_on_change("start", self.callback_js())
        self.hidden_chart.on_change("value", self.callback_py)

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

        ds = ColumnDataSource(
            data=dict(image=[image.data], x=[xmin], y=[ymin], dw=[dw], dh=[dh])
        )
        renderer = self.p.image_rgba(
            source=ds,
            image="image",
            x="x",
            y="y",
            dw="dw",
            dh="dh",
            dilate=False,
        )
        return ds, renderer

    def update_image(self, ranges):
        """
        Updates image with data returned by callback
        """
        x_range = (ranges["xmin"], ranges["xmax"])
        y_range = (ranges["ymin"], ranges["ymax"])
        dh = y_range[1] - y_range[0]
        dw = x_range[1] - x_range[0]

        image = self.callback(
            x_range, y_range, ranges["w"], ranges["h"], **self.kwargs
        )
        new_data = dict(
            image=[image.data],
            x=[x_range[0]],
            y=[y_range[0]],
            dw=[dw],
            dh=[dh],
        )

        self.ds.data.update(new_data)

    def _repr_html_(self):
        self.doc = Document()
        for m in self.p.references():
            m._document = None
        self.doc.add_root(self.p)
        return bokeh_notebook_div(self)
