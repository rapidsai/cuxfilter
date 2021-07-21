import holoviews as hv
import panel as pn
import param
import datashader as ds
from holoviews.operation.datashader import rasterize
from holoviews.element.tiles import tile_sources
import cudf

from ...constants import CUXF_DEFAULT_COLOR_PALETTE


class InteractiveDatashaderPoints(param.Parameterized):
    source_df = param.ClassSelector(
        class_=cudf.DataFrame,
        default=cudf.DataFrame(),
        doc="source cuDF dataframe",
    )
    x = param.String("x")
    y = param.String("y")
    aggregate_col = param.String()
    legend = param.Boolean(True, doc="whether to display legends or not")
    legend_position = param.String("right", doc="position of legend")
    pixel_shade_type = param.String("eq_hist")
    aggregate_fn = param.String("count")
    cmap = param.Dict(default={"cmap": CUXF_DEFAULT_COLOR_PALETTE})
    tools = param.List(
        default=["reset", "lasso_select", "wheel_zoom"],
        doc="interactive tools to add to the chart",
    )
    color_palette = param.List()
    box_stream = param.ClassSelector(
        class_=hv.streams.SelectionXY, default=hv.streams.SelectionXY()
    )
    lasso_stream = param.ClassSelector(
        class_=hv.streams.Lasso, default=hv.streams.Lasso()
    )
    reset_stream = param.ClassSelector(
        class_=hv.streams.PlotReset,
        default=hv.streams.PlotReset(resetting=False),
    )
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
        self.tiles = (
            tile_sources[self.tile_provider]()
            if (self.tile_provider is not None)
            else self.tile_provider
        )
        self._compute_datashader_assets()

    def update_points(self, data):
        self.source_df = data

    @param.depends("source_df")
    def points(self, **kwargs):
        return hv.Scatter(
            self.source_df, kdims=[self.x], vdims=[self.y, self.aggregate_col],
        )

    def add_box_select_callback(self, callback_fn):
        self.box_stream = hv.streams.SelectionXY(subscribers=[callback_fn])

    def add_lasso_select_callback(self, callback_fn):
        self.lasso_stream = hv.streams.Lasso(subscribers=[callback_fn])

    def view(self):
        ropts = dict(
            colorbar=self.legend,
            colorbar_position=self.legend_position,
            responsive=True,
            xaxis=None,
            yaxis=None,
        )
        dmap = (
            rasterize(
                hv.DynamicMap(
                    self.points,
                    streams=[
                        self.box_stream,
                        self.lasso_stream,
                        self.reset_stream,
                    ],
                ),
                aggregator=self.aggregator,
            )
            .opts(cnorm=self.pixel_shade_type, **self.cmap)
            .opts(tools=self.tools, **ropts)
        )
        return pn.pane.HoloViews(
            self.tiles * dmap if self.tiles is not None else dmap,
            sizing_mode="stretch_both",
            width_policy="fit",
        )

    def reset_all_selections(self):
        self.lasso_stream.reset()
        self.box_stream.reset()

    def add_reset_event(self, callback_fn):
        self.reset_stream = hv.streams.PlotReset(subscribers=[callback_fn])
