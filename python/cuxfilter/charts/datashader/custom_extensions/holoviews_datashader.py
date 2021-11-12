import holoviews as hv
import panel as pn
import param
import datashader as ds
import numpy as np
import cudf
import cupy
from holoviews.element.tiles import tile_sources
from holoviews.operation.datashader import SpreadingOperation, rasterize
from bokeh.models import (
    LinearColorMapper,
    LogColorMapper,
    BasicTicker,
    ColorBar,
    BinnedTicker,
)
from datashader import transfer_functions as tf
from ...constants import CUXF_DEFAULT_COLOR_PALETTE


def _rect_vertical_mask(px):
    """
    Produce a vertical rectangle mask with truth
    values in ``(2 * px + 1) * ((2 * px + 1)/2)``
    """
    px = int(px)
    w = 2 * px + 1
    zero_bool = np.zeros((w, px), dtype="bool")
    x_bool = np.ones((w, w - px), dtype="bool")
    return np.concatenate((x_bool, zero_bool), axis=1)


def _rect_horizontal_mask(px):
    """
    Produce a horizontal rectangle mask with truth
    values in ``((2 * px + 1)/2) * (2 * px + 1)``
    """
    px = int(px)
    w = 2 * px + 1
    zero_bool = np.zeros((px, w), dtype="bool")
    x_bool = np.ones((w - px, w), dtype="bool")
    return np.concatenate((x_bool, zero_bool), axis=0)


def _cross_mask(px):
    """
    Produce a cross symbol mask with truth
    values in ``((2 * px + 1)/2) * (2 * px + 1)``
    """

    px = int(px)
    w = 2 * px + 1
    zero_bool = np.zeros((w, w), dtype="bool")
    np.fill_diagonal(zero_bool, True)
    np.fill_diagonal(np.fliplr(zero_bool), True)
    return zero_bool


ds.transfer_functions._mask_lookup["rect_vertical"] = _rect_vertical_mask
ds.transfer_functions._mask_lookup["rect_horizontal"] = _rect_horizontal_mask
ds.transfer_functions._mask_lookup["cross"] = _cross_mask

_color_mapper = {
    "linear": LinearColorMapper,
    "log": LogColorMapper,
}


def _generate_legend(
    pixel_shade_type, color_palette, legend_title, constant_limit,
):
    mapper = _color_mapper[pixel_shade_type](
        palette=color_palette, low=constant_limit[0], high=constant_limit[1]
    )
    color_bar = ColorBar(
        color_mapper=mapper,
        location=(0, 0),
        ticker=BasicTicker(desired_num_ticks=len(color_palette))
        if pixel_shade_type != "eq_hist"
        else BinnedTicker(mapper=mapper, num_major_ticks=len(color_palette)),
        title=legend_title,
    )
    return color_bar


def _get_legend_title(aggregate_fn, aggregate_col):
    if aggregate_fn == "count":
        return aggregate_fn
    else:
        return aggregate_fn + " " + aggregate_col


class dynspread(SpreadingOperation):
    """
    datashader has a pending change to support internally converting
    cupy arrays to numpy(https://github.com/holoviz/datashader/pull/1015)

    This class is a custom implmentation of
    https://github.com/holoviz/holoviews/blob/master/holoviews/operation/datashader.py#L1660
    to support the cupy array internal conversion until datashader merges the
    changes
    """

    max_px = param.Integer(
        default=3,
        doc="""
        Maximum number of pixels to spread on all sides.""",
    )

    threshold = param.Number(
        default=0.5,
        bounds=(0, 1),
        doc="""
        When spreading, determines how far to spread.
        Spreading starts at 1 pixel, and stops when the fraction
        of adjacent non-empty pixels reaches this threshold.
        Higher values give more spreading, up to the max_px
        allowed.""",
    )
    shape = param.ObjectSelector(
        default="circle",
        objects=[
            "circle",
            "square",
            "rect_vertical",
            "rect_horizontal",
            "cross",
        ],
    )

    def _apply_spreading(self, array):
        if cupy and isinstance(array.data, cupy.ndarray):
            # Convert img.data to numpy array before passing to nb.jit kernels
            array.data = cupy.asnumpy(array.data)
        return tf.dynspread(
            array,
            max_px=self.p.max_px,
            threshold=self.p.threshold,
            how=self.p.how,
            shape=self.p.shape,
        )


class InteractiveDatashader(param.Parameterized):
    source_df = param.ClassSelector(
        class_=cudf.DataFrame,
        default=cudf.DataFrame(),
        doc="source cuDF dataframe",
    )
    x = param.String("x")
    y = param.String("y")
    width = param.Integer(400)
    height = param.Integer(400)
    pixel_shade_type = param.String("linear")
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
    spread_threshold = param.Number(
        0, doc="threshold parameter passed to dynspread function"
    )
    tile_provider = param.String(None)

    @property
    def vdims(self):
        if self.aggregate_col is None:
            return [self.y]
        return [self.y, self.aggregate_col]

    def __init__(self, **params):
        """
        initialize InteractiveDatashader object, and set a listener on
        self.data
        """
        super(InteractiveDatashader, self).__init__(**params)
        self.tiles = (
            tile_sources[self.tile_provider]()
            if (self.tile_provider is not None)
            else self.tile_provider
        )

    def add_box_select_callback(self, callback_fn):
        self.box_stream = hv.streams.SelectionXY(subscribers=[callback_fn])

    def add_lasso_select_callback(self, callback_fn):
        self.lasso_stream = hv.streams.Lasso(subscribers=[callback_fn])

    def reset_all_selections(self):
        self.lasso_stream.reset()
        self.box_stream.reset()

    def add_reset_event(self, callback_fn):
        self.reset_stream = hv.streams.PlotReset(subscribers=[callback_fn])


class InteractiveDatashaderPoints(InteractiveDatashader):
    aggregate_col = param.String(allow_None=True)
    aggregate_fn = param.String("count")
    legend = param.Boolean(True, doc="whether to display legends or not")
    legend_position = param.String("right", doc="position of legend")
    cmap = param.Dict(default={"cmap": CUXF_DEFAULT_COLOR_PALETTE})
    tools = param.List(
        default=["reset", "lasso_select", "wheel_zoom"],
        doc="interactive tools to add to the chart",
    )
    color_palette = param.List()
    point_shape = param.ObjectSelector(
        default="circle",
        objects=[
            "circle",
            "square",
            "rect_vertical",
            "rect_horizontal",
            "cross",
        ],
    )
    max_px = param.Integer(10)
    clims = param.Tuple(default=(None, None))

    def __init__(self, **params):
        super(InteractiveDatashaderPoints, self).__init__(**params)
        self._compute_datashader_assets()

    def _compute_clims(self):
        if not isinstance(
            self.source_df[self.aggregate_col].dtype,
            cudf.core.dtypes.CategoricalDtype,
        ):
            self.clims = (
                self.source_df[
                    self.aggregate_col
                    if self.aggregate_col is not None
                    else self.y
                ].min(),
                self.source_df[
                    self.aggregate_col
                    if self.aggregate_col is not None
                    else self.y
                ].max(),
            )

    def _compute_datashader_assets(self):
        self.aggregator = None
        self.cmap = {"cmap": self.color_palette}
        if isinstance(
            self.source_df[self.aggregate_col].dtype,
            cudf.core.dtypes.CategoricalDtype,
        ):
            self.cmap = {
                "color_key": {
                    k: v
                    for k, v in zip(
                        list(
                            self.source_df[
                                self.aggregate_col
                            ].cat.categories.to_pandas()
                        ),
                        self.color_palette,
                    )
                }
            }

        if self.aggregate_fn:
            self.aggregator = getattr(ds, self.aggregate_fn)(
                self.aggregate_col
            )

        self._compute_clims()

    def update_data(self, data):
        self.source_df = data
        self._compute_clims()

    @param.depends("source_df")
    def points(self, **kwargs):
        return hv.Scatter(self.source_df, kdims=[self.x], vdims=self.vdims)

    def get_chart(self, streams=[]):
        dmap = rasterize(
            hv.DynamicMap(self.points, streams=streams),
            aggregator=self.aggregator,
        ).opts(
            cnorm=self.pixel_shade_type,
            **self.cmap,
            colorbar=self.legend,
            nodata=0,
            colorbar_position=self.legend_position,
            tools=self.tools,
            active_tools=["wheel_zoom", "pan"],
        )
        if self.aggregate_fn != "count":
            dmap = dmap.opts(clim=self.clims)

        return dmap

    def view(self):
        dmap = dynspread(
            self.get_chart(
                streams=[
                    self.box_stream,
                    self.lasso_stream,
                    self.reset_stream,
                ]
            ),
            threshold=self.spread_threshold,
            shape=self.point_shape,
            max_px=self.max_px,
        ).opts(xaxis=None, yaxis=None, responsive=True, tools=[])

        return pn.pane.HoloViews(
            self.tiles * dmap if self.tiles is not None else dmap,
            sizing_mode="stretch_both",
            height=self.height,
        )


class InteractiveDatashaderLine(InteractiveDatashader):
    color = param.String()
    transparency = param.Number(0, bounds=(0, 1))

    tools = param.List(
        default=["reset", "lasso_select", "wheel_zoom"],
        doc="interactive tools to add to the chart",
    )

    def __init__(self, **params):
        super(InteractiveDatashaderLine, self).__init__(**params)

    def update_data(self, data):
        self.source_df = data

    @param.depends("source_df")
    def line(self, **kwargs):
        return hv.Curve(self.source_df, kdims=[self.x], vdims=[self.y])

    def get_chart(self, streams=[]):
        return rasterize(hv.DynamicMap(self.line, streams=streams),).opts(
            cmap=[self.color]
        )

    def view(self):
        dmap = dynspread(
            self.get_chart(
                streams=[
                    self.box_stream,
                    self.lasso_stream,
                    self.reset_stream,
                ]
            )
        ).opts(tools=self.tools, xaxis=None, yaxis=None, responsive=True)

        return pn.pane.HoloViews(
            self.tiles * dmap if self.tiles is not None else dmap,
            sizing_mode="stretch_both",
            height=self.height,
        )


class InteractiveDatashaderGraph(param.Parameterized):
    nodes_df = param.ClassSelector(
        class_=cudf.DataFrame,
        default=cudf.DataFrame(),
        doc="nodes cuDF dataframe",
    )
    edges_df = param.ClassSelector(
        class_=cudf.DataFrame,
        default=cudf.DataFrame(),
        doc="edges cuDF dataframe",
    )
    node_x = param.String("x")
    node_y = param.String("y")
    width = param.Integer(400)
    height = param.Integer(400)
    node_pixel_shade_type = param.String("linear")
    node_spread_threshold = param.Number(
        0, doc="threshold parameter passed to dynspread function"
    )
    tile_provider = param.String(None)
    node_aggregate_col = param.String(allow_None=True)
    node_aggregate_fn = param.String("count")
    legend = param.Boolean(True, doc="whether to display legends or not")
    legend_position = param.String("right", doc="position of legend")
    node_cmap = param.Dict(default={"cmap": CUXF_DEFAULT_COLOR_PALETTE})
    tools = param.List(
        default=["reset", "lasso_select", "wheel_zoom"],
        doc="interactive tools to add to the chart",
    )
    node_color_palette = param.List()
    node_point_shape = param.ObjectSelector(
        default="circle",
        objects=[
            "circle",
            "square",
            "rect_vertical",
            "rect_horizontal",
            "cross",
        ],
    )
    node_max_px = param.Integer(10)
    node_clims = param.Tuple(default=(None, None))
    edge_color = param.String()
    edge_source = param.String("src")
    edge_target = param.String("dst")
    edge_transparency = param.Number(0, bounds=(0, 1))
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

    def update_color_palette(self, value):
        self.node_color_palette = value
        self.nodes_chart.color_palette = value

    def __init__(self, **params):
        super(InteractiveDatashaderGraph, self).__init__(**params)
        self.tiles = (
            tile_sources[self.tile_provider]()
            if (self.tile_provider is not None)
            else self.tile_provider
        )
        self.nodes_chart = InteractiveDatashaderPoints(
            source_df=self.nodes_df,
            x=self.node_x,
            y=self.node_y,
            aggregate_col=self.node_aggregate_col,
            aggregate_fn=self.node_aggregate_fn,
            color_palette=self.node_color_palette,
            pixel_shade_type=self.node_pixel_shade_type,
            tile_provider=self.tile_provider,
            legend=self.legend,
            legend_position=self.legend_position,
            spread_threshold=self.node_spread_threshold,
            point_shape=self.node_point_shape,
            max_px=self.node_max_px,
        )

        self.edges_chart = InteractiveDatashaderLine(
            source_df=self.edges_df,
            x=self.edge_source,
            y=self.edge_target,
            color=self.edge_color,
            transparency=self.edge_transparency,
        )

    def update_data(self, nodes, edges=None):
        self.nodes_chart.update_data(nodes)
        if edges:
            self.edges_chart.update_data(edges)

    def view(self):
        dmap_nodes = dynspread(
            self.nodes_chart.get_chart(
                streams=[
                    self.box_stream,
                    self.lasso_stream,
                    self.reset_stream,
                ]
            ),
            threshold=self.node_spread_threshold,
            shape=self.node_point_shape,
            max_px=self.node_max_px,
        ).opts(xaxis=None, yaxis=None, responsive=True, tools=[])

        dmap_edges = dynspread(self.edges_chart.get_chart()).opts(
            tools=self.tools, xaxis=None, yaxis=None, responsive=True
        )

        return pn.pane.HoloViews(
            self.tiles * dmap_edges * dmap_nodes
            if self.tiles is not None
            else dmap_edges * dmap_nodes,
            sizing_mode="stretch_both",
            height=self.height,
        )

    def add_box_select_callback(self, callback_fn):
        self.box_stream = hv.streams.SelectionXY(subscribers=[callback_fn])

    def add_lasso_select_callback(self, callback_fn):
        self.lasso_stream = hv.streams.Lasso(subscribers=[callback_fn])

    def reset_all_selections(self):
        self.lasso_stream.reset()
        self.box_stream.reset()

    def add_reset_event(self, callback_fn):
        self.reset_stream = hv.streams.PlotReset(subscribers=[callback_fn])
