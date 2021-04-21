from ..core.non_aggregate import (
    BaseScatter,
    BaseLine,
    BaseStackedLine,
    BaseGraph,
)
from .custom_extensions import (
    InteractiveImage,
    CustomInspectTool,
    calc_connected_edges,
)

from distutils.version import LooseVersion
import datashader as ds
from datashader import transfer_functions as tf
import dask_cudf
import dask.dataframe as dd
import numpy as np
import cupy as cp
import pandas as pd
import bokeh
import cudf
from bokeh import events
from bokeh.plotting import figure
from bokeh.models import (
    BoxSelectTool,
    ColorBar,
    LassoSelectTool,
    LinearColorMapper,
    LogColorMapper,
    BasicTicker,
    FixedTicker,
)
from bokeh.tile_providers import get_provider
from PIL import Image
import requests
from io import BytesIO

ds_version = LooseVersion(ds.__version__)

_color_mapper = {"linear": LinearColorMapper, "log": LogColorMapper}


def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


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


def _compute_datashader_assets(
    data, x, aggregate_col, aggregate_fn, color_palette
):
    aggregator = None
    cmap = {"cmap": color_palette}

    if isinstance(data[x].dtype, cudf.core.dtypes.CategoricalDtype):
        if ds_version >= "0.11":
            aggregator = ds.by(x, getattr(ds, aggregate_fn)(aggregate_col),)
        else:
            print("only count_cat supported by datashader <=0.10")
            aggregator = ds.count_cat(x)
        cmap = {
            "color_key": {
                k: v
                for k, v in zip(list(data[x].cat.categories), color_palette,)
            }
        }
    else:
        if aggregate_fn:
            aggregator = getattr(ds, aggregate_fn)(aggregate_col)
    return aggregator, cmap


def _get_provider(tile_provider):
    if tile_provider is None:
        return None
    elif isinstance(tile_provider, str):
        return get_provider(tile_provider)
    elif isinstance(tile_provider, bokeh.models.tiles.WMTSTileSource):
        return tile_provider
    return None


def _get_legend_title(aggregate_fn, aggregate_col):
    if aggregate_fn == "count":
        return aggregate_fn
    else:
        return aggregate_fn + " " + aggregate_col


def _generate_legend(
    pixel_shade_type,
    color_palette,
    legend_title,
    constant_limit,
    color_bar=None,
    update=False,
):
    mapper = _color_mapper[pixel_shade_type](
        palette=color_palette, low=constant_limit[0], high=constant_limit[1]
    )
    if update and color_bar:
        color_bar.color_mapper = mapper
        return color_bar

    color_bar = ColorBar(
        color_mapper=mapper,
        location=(0, 0),
        ticker=BasicTicker(desired_num_ticks=len(color_palette)),
        title=legend_title,
    )
    return color_bar


ds.transfer_functions._mask_lookup["rect_vertical"] = _rect_vertical_mask
ds.transfer_functions._mask_lookup["rect_horizontal"] = _rect_horizontal_mask


class Scatter(BaseScatter):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    constant_limit = None
    color_bar = None
    legend_added = False

    def format_source_data(self, data):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        self.source = data

    def show_legend(self):
        return self.legend and (
            self.pixel_shade_type in list(_color_mapper.keys())
        )

    def render_legend(self):
        if self.show_legend():
            update = self.color_bar is not None
            self.color_bar = _generate_legend(
                self.pixel_shade_type,
                self.color_palette,
                _get_legend_title(self.aggregate_fn, self.aggregate_col),
                self.constant_limit,
                color_bar=self.color_bar,
                update=update,
            )
            if (update and self.legend_added) is False:
                self.chart.add_layout(self.color_bar, self.legend_position)
                self.legend_added = True

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(
            x_range, y_range, w, h, data_source, **kwargs
        ):
            dd = data_source[[self.x, self.y, self.aggregate_col]]
            dd[self.x] = self._to_xaxis_type(dd[self.x])
            dd[self.y] = self._to_yaxis_type(dd[self.y])

            x_range = self._to_xaxis_type(x_range)
            y_range = self._to_yaxis_type(y_range)

            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            aggregator, cmap = _compute_datashader_assets(
                dd,
                self.x,
                self.aggregate_col,
                self.aggregate_fn,
                self.color_palette,
            )
            agg = cvs.points(dd, self.x, self.y, aggregator,)

            if self.constant_limit is None or self.aggregate_fn == "count":
                self.constant_limit = [
                    float(cp.nanmin(agg.data)),
                    float(cp.nanmax(agg.data)),
                ]
                self.render_legend()

            span = {"span": self.constant_limit}
            if self.pixel_shade_type == "eq_hist":
                span = {}

            img = tf.shade(agg, how=self.pixel_shade_type, **cmap, **span)

            if self.pixel_spread == "dynspread":
                return tf.dynspread(
                    img,
                    threshold=self.pixel_density,
                    max_px=self.point_size,
                    shape=self.point_shape,
                )
            else:
                return tf.spread(
                    img, px=self.point_size, shape=self.point_shape
                )

        return viewInteractiveImage

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if len(self.title) == 0:
            self.title = (
                "Scatter plot for "
                + self.aggregate_col
                + " "
                + self.aggregate_fn
            )

        self.chart = figure(
            toolbar_location="right",
            tools="pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
            x_range=self.x_range,
            y_range=self.y_range,
            width=self.width,
            height=self.height,
        )

        self.chart.add_tools(BoxSelectTool())
        self.chart.add_tools(LassoSelectTool())

        self.tile_provider = _get_provider(self.tile_provider)
        if self.tile_provider is not None:
            self.chart.add_tile(self.tile_provider)
            self.chart.axis.visible = False
        # reset legend and color_bar
        self.legend_added = False
        self.color_bar = None

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
            timeout=self.timeout,
            x_dtype=self.x_dtype,
            y_dtype=self.y_dtype,
        )

        if self.legend_added is False:
            self.render_legend()

    def update_dimensions(self, width=None, height=None):
        """
        Description:


        Input:



        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def reload_chart(self, data=None, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in data.columns})
            self.interactive_image.update_chart(data_source=data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        self.add_event(events.SelectionGeometry, callback)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.colors_set:
            self.default_palette = theme.color_palette
            self.render_legend()
            self.interactive_image.update_chart()


class Graph(BaseGraph):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "node_y"
    data_x_axis = "node_x"
    image = None
    constant_limit_nodes = None
    constant_limit_edges = None
    color_bar = None
    legend_added = False

    def compute_colors(self):
        if self.node_color_palette is None:
            self.node_color_palette = bokeh.palettes.Purples9

        BREAKS = np.linspace(
            self.nodes[self.node_aggregate_col].min(),
            self.nodes[self.node_aggregate_col].max(),
            len(self.node_color_palette),
        )

        x = self.source.data[self.node_aggregate_col]
        inds = pd.cut(x, BREAKS, labels=False, include_lowest=True)
        colors = [self.node_color_palette[i] for i in inds]
        self.source.data[self.node_aggregate_col] = colors

    def show_legend(self):
        """
        return if legend=True and pixel_shade_type is ['linear', 'log']
        """
        return self.legend and (
            self.node_pixel_shade_type in list(_color_mapper.keys())
        )

    def render_legend(self):
        """
        render legend
        """
        if self.show_legend():
            update = self.color_bar is not None
            self.color_bar = _generate_legend(
                self.node_pixel_shade_type,
                self.node_color_palette,
                _get_legend_title(
                    self.node_aggregate_fn, self.node_aggregate_col
                ),
                self.constant_limit_nodes,
                color_bar=self.color_bar,
                update=update,
            )
            if (update and self.legend_added) is False:
                self.chart.add_layout(self.color_bar, self.legend_position)
                self.legend_added = True

    def nodes_plot(self, canvas, nodes, name=None):
        """
        plot nodes(scatter)
        """
        aggregator, cmap = _compute_datashader_assets(
            nodes,
            self.node_id,
            self.node_aggregate_col,
            self.node_aggregate_fn,
            self.node_color_palette,
        )

        agg = canvas.points(
            nodes.sort_index(), self.node_x, self.node_y, aggregator
        )

        if (
            self.constant_limit_nodes is None
            or self.node_aggregate_fn == "count"
        ):
            self.constant_limit_nodes = [
                float(cp.nanmin(agg.data)),
                float(cp.nanmax(agg.data)),
            ]
            self.render_legend()

        span = {"span": self.constant_limit_nodes}
        if self.node_pixel_shade_type == "eq_hist":
            span = {}

        return getattr(tf, self.node_pixel_spread)(
            tf.shade(
                agg, how=self.node_pixel_shade_type, name=name, **cmap, **span
            ),
            threshold=self.node_pixel_density,
            max_px=self.node_point_size,
            shape=self.node_point_shape,
        )

    def edges_plot(self, canvas, nodes, name=None):
        """
        plot edges(lines)
        """
        aggregator, cmap = _compute_datashader_assets(
            self.connected_edges,
            self.node_x,
            self.edge_aggregate_col,
            self.edge_aggregate_fn,
            self.edge_color_palette,
        )

        agg = canvas.line(
            self.connected_edges, self.node_x, self.node_y, aggregator
        )

        if (
            self.constant_limit_edges is None
            or self.edge_aggregate_fn == "count"
        ):
            self.constant_limit_edges = [
                float(cp.nanmin(agg.data)),
                float(cp.nanmax(agg.data)),
            ]

        span = {"span": self.constant_limit_nodes}

        return getattr(tf, self.node_pixel_spread)(
            tf.shade(
                agg,
                name=name,
                how="linear",
                alpha=255 - 255 * self.edge_transparency,
                **cmap,
                **span,
            ),
            max_px=1,
        )

    def format_source_data(self, dataframe):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        if isinstance(dataframe, cudf.core.DataFrame):
            self.nodes = dataframe
        else:
            self.nodes = dataframe.data
            self.edges = dataframe.edges

        if self.edges is not None:
            # update connected_edges value for datashaded edges
            self.connected_edges = calc_connected_edges(
                self.nodes,
                self.edges,
                self.node_x,
                self.node_y,
                self.node_id,
                self.edge_source,
                self.edge_target,
                self.edge_aggregate_col,
                self.x_dtype,
                self.y_dtype,
                self.edge_render_type,
                self.curve_params,
            )

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(
            x_range,
            y_range,
            w,
            h,
            data_source=self.nodes,
            nodes_plot=self.nodes_plot,
            edges_plot=self.edges_plot,
            chart=self.chart,
            **kwargs,
        ):
            dd = data_source[
                [
                    self.node_id,
                    self.node_x,
                    self.node_y,
                    self.node_aggregate_col,
                ]
            ]
            dd[self.node_x] = self._to_xaxis_type(dd[self.node_x])
            dd[self.node_y] = self._to_yaxis_type(dd[self.node_y])

            x_range = self._to_xaxis_type(x_range)
            y_range = self._to_yaxis_type(y_range)

            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            plot = None
            if self.source is not None:
                self.source.data = {
                    self.node_x: [],
                    self.node_y: [],
                    self.node_aggregate_col: [],
                    self.node_aggregate_col + "_color": [],
                }
            np = nodes_plot(cvs, dd)
            if self.display_edges._active:
                ep = edges_plot(cvs, dd)
                plot = tf.stack(ep, np, how="over")
            else:
                plot = np

            return plot

        return viewInteractiveImage

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if len(self.title) == 0:
            self.title = "Graph"
        self.x_range = (
            self.x_range[0] - self.node_point_size,
            self.x_range[1] + self.node_point_size,
        )
        self.y_range = (
            self.y_range[0] - self.node_point_size,
            self.y_range[1] + self.node_point_size,
        )
        self.chart = figure(
            toolbar_location="right",
            tools="pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
            x_range=self.x_range,
            y_range=self.y_range,
            width=self.width,
            height=self.height,
        )

        self.tile_provider = _get_provider(self.tile_provider)
        if self.tile_provider is not None:
            self.chart.add_tile(self.tile_provider)
            self.chart.axis.visible = False
        # reset legend and color_bar
        self.legend_added = False
        self.color_bar = None
        # loading icon from a url
        impath = (
            "https://raw.githubusercontent.com/rapidsai/cuxfilter/"
            + "branch-0.15/python/cuxfilter/charts/datashader/icons/graph.png"
        )

        self.inspect_neighbors = CustomInspectTool(
            icon=load_image(impath),
            _active=True,
            tool_name="Inspect Neighboring Edges",
        )
        # loading icon from a url
        impath = (
            "https://raw.githubusercontent.com/rapidsai/cuxfilter/"
            + "branch-0.15/python/cuxfilter/charts/datashader/icons/XPan.png"
        )
        self.display_edges = CustomInspectTool(
            icon=load_image(impath), _active=True, tool_name="Display Edges"
        )

        def cb(attr, old, new):
            if new:
                self.connected_edges = calc_connected_edges(
                    self.interactive_image.kwargs["data_source"],
                    self.edges,
                    self.node_x,
                    self.node_y,
                    self.node_id,
                    self.edge_source,
                    self.edge_target,
                    self.edge_aggregate_col,
                    self.x_dtype,
                    self.y_dtype,
                    self.edge_render_type,
                    self.curve_params,
                )
            self.interactive_image.update_chart()

        self.display_edges.on_change("_active", cb)

        self.chart.add_tools(BoxSelectTool())
        self.chart.add_tools(LassoSelectTool())
        self.chart.add_tools(self.inspect_neighbors)
        self.chart.add_tools(self.display_edges)

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.nodes,
            timeout=self.timeout,
            x_dtype=self.x_dtype,
            y_dtype=self.y_dtype,
        )

        if self.legend_added is False:
            self.render_legend()

    def update_dimensions(self, width=None, height=None):
        """
        Description:


        Input:



        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def reload_chart(self, data, edges=None, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in self.nodes.columns})

            # update connected_edges value for datashaded edges
            # if display edge toggle is active
            if self.display_edges._active:
                self.connected_edges = calc_connected_edges(
                    data,
                    self.edges if edges is None else edges,
                    self.node_x,
                    self.node_y,
                    self.node_id,
                    self.edge_source,
                    self.edge_target,
                    self.edge_aggregate_col,
                    self.x_dtype,
                    self.y_dtype,
                    self.edge_render_type,
                    self.curve_params,
                )

            self.interactive_image.update_chart(data_source=data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        self.add_event(events.SelectionGeometry, callback)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.colors_set:
            self.default_palette = theme.color_palette
            self.render_legend()
            self.interactive_image.update_chart()


class Line(BaseLine):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    use_data_tiles = False

    def calculate_source(self, data):
        """
        Description:

        -------------------------------------------
        Input:
        data = cudf.DataFrame
        -------------------------------------------

        Ouput:
        """
        self.format_source_data(data)

    def format_source_data(self, data):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        self.source = data

        self.x_range = (self.source[self.x].min(), self.source[self.x].max())
        self.y_range = (self.source[self.y].min(), self.source[self.y].max())

        if isinstance(data, dask_cudf.core.DataFrame):
            self.x_range = dd.compute(*self.x_range)
            self.y_range = dd.compute(*self.y_range)

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(
            x_range, y_range, w, h, data_source, **kwargs
        ):
            dd = data_source[[self.x, self.y]]
            dd[self.x] = self._to_xaxis_type(dd[self.x])
            dd[self.y] = self._to_yaxis_type(dd[self.y])

            x_range = self._to_xaxis_type(x_range)
            y_range = self._to_yaxis_type(y_range)

            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )

            agg = cvs.line(source=dd, x=self.x, y=self.y)

            img = tf.shade(
                agg, cmap=["white", self.color], how=self.pixel_shade_type
            )
            return img

        return viewInteractiveImage

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if len(self.title) == 0:
            if self.x == self.y:
                self.title = "Line plot for " + self.x
            else:
                self.title = "Line plot for (" + self.x + "," + self.y + ")"

        self.chart = figure(
            toolbar_location="right",
            tools="pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
            x_range=self.x_range,
            y_range=self.y_range,
            width=self.width,
            height=self.height,
        )

        self.chart.add_tools(BoxSelectTool())
        self.chart.axis.visible = True
        if self.x_axis_tick_formatter:
            self.chart.xaxis.formatter = self.x_axis_tick_formatter
        if self.y_axis_tick_formatter:
            self.chart.yaxis.formatter = self.y_axis_tick_formatter
        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
            timeout=self.timeout,
            x_dtype=self.x_dtype,
            y_dtype=self.y_dtype,
        )

    def update_dimensions(self, width=None, height=None):
        """
        Description:


        Input:



        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def reload_chart(self, data, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in data.columns})
            self.interactive_image.update_chart(data_source=data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        self.add_event(events.SelectionGeometry, callback)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.color_set:
            self.default_color = theme.chart_color
            self.interactive_image.update_chart()


class StackedLines(BaseStackedLine):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    use_data_tiles = False
    color_bar = None
    legend_added = False

    def render_legend(self):
        if self.legend:
            mapper = LinearColorMapper(
                palette=self.colors, low=1, high=len(self.y)
            )
            self.color_bar = ColorBar(
                color_mapper=mapper,
                location=(0, 0),
                ticker=FixedTicker(ticks=list(range(1, len(self.y) + 1))),
                major_label_overrides=dict(
                    zip(list(range(1, len(self.y) + 1)), self.y)
                ),
                major_label_text_baseline="top",
                major_label_text_align="left",
                major_tick_in=0,
                major_tick_out=0,
            )
            if self.legend_added is False:
                self.chart.add_layout(self.color_bar, self.legend_position)
                self.legend_added = True

    def calculate_source(self, data):
        """
        Description:

        -------------------------------------------
        Input:
        data = cudf.DataFrame
        -------------------------------------------

        Ouput:
        """
        self.format_source_data(data)

    def format_source_data(self, data):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        self.source = data
        if self.x_range is None:
            self.x_range = (
                self.source[self.x].min(),
                self.source[self.x].max(),
            )
        if self.y_range is None:
            # cudf_df[['a','b','c']].min().min() gives min value
            # between all values in columns a,b and c

            self.y_range = (
                self.source[self.y].min().min(),
                self.source[self.y].max().max(),
            )
        if isinstance(data, dask_cudf.core.DataFrame):
            self.x_range = dd.compute(*self.x_range)
            self.y_range = dd.compute(*self.y_range)

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(
            x_range, y_range, w, h, data_source, **kwargs
        ):
            dd = data_source[[self.x] + self.y]
            dd[self.x] = self._to_xaxis_type(dd[self.x])
            for _y in self.y:
                dd[_y] = self._to_yaxis_type(dd[_y])

            x_range = self._to_xaxis_type(x_range)
            y_range = self._to_yaxis_type(y_range)

            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            aggs = dict((_y, cvs.line(dd, x=self.x, y=_y)) for _y in self.y)
            imgs = [
                tf.shade(aggs[_y], cmap=["white", color])
                for _y, color in zip(self.y, self.colors)
            ]
            return tf.stack(*imgs)

        return viewInteractiveImage

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if len(self.title) == 0:
            self.title = "Stacked Line plots on x-axis: " + self.x

        self.chart = figure(
            toolbar_location="right",
            tools="pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
            x_range=self.x_range,
            y_range=self.y_range,
            width=self.width,
            height=self.height,
            **self.library_specific_params,
        )

        self.chart.add_tools(BoxSelectTool(dimensions="width"))
        # reset legend and color_bar
        self.legend_added = False
        self.color_bar = None

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        if self.x_axis_tick_formatter:
            self.chart.xaxis.formatter = self.x_axis_tick_formatter
        if self.y_axis_tick_formatter:
            self.chart.yaxis.formatter = self.y_axis_tick_formatter

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
            timeout=self.timeout,
            x_dtype=self.x_dtype,
            y_dtype=self.y_dtype,
        )

        if self.legend_added is False:
            self.render_legend()

    def update_dimensions(self, width=None, height=None):
        """
        Description:


        Input:



        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def reload_chart(self, data, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in data.columns})
            self.interactive_image.update_chart(data_source=data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        self.add_event(events.SelectionGeometry, callback)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.colors_set:
            self.default_colors = [theme.chart_color]
            self.interactive_image.update_chart()
            self.legend_added = False
            self.render_legend()
