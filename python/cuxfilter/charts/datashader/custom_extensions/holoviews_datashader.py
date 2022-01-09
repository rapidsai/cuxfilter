import holoviews as hv
import panel as pn
import param
import datashader as ds
from holoviews.operation.datashader import datashade
from holoviews.element.tiles import tile_sources
import cudf

opts = dict(
    width=1000,
    height=600,
    xaxis=None,
    yaxis=None,
    bgcolor="black",
    show_grid=False,
)


class InteractiveDatashaderPoints(param.Parameterized):
    source_df = param.ClassSelector(
        class_=cudf.DataFrame, doc="source cuDF dataframe",
    )
    points = hv.Scatter(data=[])
    x = param.String("x")
    y = param.String("y")
    aggregate_col = param.String()
    pixel_shade_type = param.String("eq_hist")
    aggregate_fn = param.String("count")
    cmap = param.Dict()
    default_tools = param.List(
        default=["reset", "save", "hover", "lasso_select", "wheel_zoom"],
        doc="interactive tools to add to the chart",
    )
    width = param.Integer(default=400, doc="width of the chart")
    height = param.Integer(default=400, doc="height of the chart")
    color_palette = param.List()
    streams = [
        hv.streams.SelectionXY(),
        hv.streams.Lasso(),
        hv.streams.PlotReset(),
    ]
    tile_provider = param.String(None)

    def _compute_datashader_assets(self):
        self.aggregator = None
        self.cmap = {"cmap": self.color_palette}
        if isinstance(
            self.source_df[self.x].dtype, cudf.core.dtypes.CategoricalDtype
        ):
            self.aggregator = ds.by(
                self.x, getattr(ds, self.aggregate_fn)(self.aggregate_col)
            )
            self.cmap = {
                "color_key": {
                    k: v
                    for k, v in zip(
                        list(self.source_df[self.x].cat.categories),
                        self.color_palette,
                    )
                }
            }
        else:
            if self.aggregate_fn:
                self.aggregator = getattr(ds, self.aggregate_fn)(
                    self.aggregate_col
                )

    def __init__(self, **params):
        """
        initialize pydeck object, and set a listener on self.data
        """
        super(InteractiveDatashaderPoints, self).__init__(**params)
        self.points = hv.Scatter(
            self.source_df, kdims=[self.x], vdims=[self.y, self.aggregate_col]
        )
        self.tiles = (
            tile_sources[self.tile_provider]()
            if (self.tile_provider is not None)
            else self.tile_provider
        )
        self._compute_datashader_assets()

    def update_points(self, data):
        self.points.data = data

    def add_box_select_callback(self, callback_fn):
        box_select = hv.streams.SelectionXY(source=self.points)
        box_select.add_subscriber(callback_fn)
        self.streams[0] = box_select
        self.points.streams = self.streams

    def add_lasso_select_callback(self, callback_fn):
        lasso_select = hv.streams.Lasso(source=self.points)
        lasso_select.add_subscriber(callback_fn)
        self.streams[1] = lasso_select
        self.points.streams = self.streams

    def view(self):
        agg = datashade(
            self.points,
            cnorm=self.pixel_shade_type,
            aggregator=self.aggregator,
            **self.cmap,
        ).opts(default_tools=self.default_tools)
        return pn.pane.HoloViews(
            self.tiles * agg if self.tiles is not None else agg,
            width=self.width,
            height=self.height,
        )

    def add_reset_event(self, callback_fn):
        reset = hv.streams.PlotReset()
        reset.add_subscriber(callback_fn)
        self.streams[2] = reset
        self.points.streams = self.streams
