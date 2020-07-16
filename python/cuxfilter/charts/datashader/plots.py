from ..core.non_aggregate import (
    BaseScatter,
    BaseLine,
    BaseStackedLine,
    BaseGraph,
)
from .custom_extensions import InteractiveImage
from distutils.version import LooseVersion

import datashader as ds
from datashader import transfer_functions as tf
from datashader.colors import Hot
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
    ColumnDataSource,
    ColorBar,
    LinearColorMapper,
    LogColorMapper,
    BasicTicker,
    FixedTicker,
)
from bokeh.tile_providers import get_provider

ds_version = LooseVersion(ds.__version__)

_color_mapper = {"linear": LinearColorMapper, "log": LogColorMapper}


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
    elif type(tile_provider) == str:
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
        background_fill_alpha=0,
    )
    return color_bar


ds.transfer_functions._mask_lookup["rect_vertical"] = _rect_vertical_mask
ds.transfer_functions._mask_lookup["rect_horizontal"] = _rect_horizontal_mask


class Scatter(BaseScatter):
    """
        Description:
    """

    chart_type: str = "scatter"
    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    no_colors_set = False
    constant_limit = None
    color_bar = None

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
            if update is False:
                self.chart.add_layout(self.color_bar, self.legend_position)

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            aggregator, cmap = _compute_datashader_assets(
                data_source,
                self.x,
                self.aggregate_col,
                self.aggregate_fn,
                self.color_palette,
            )

            agg = cvs.points(data_source, self.x, self.y, aggregator,)

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
        if self.color_palette is None:
            self.no_colors_set = True
            self.color_palette = Hot

        if len(self.title) == 0:
            self.title = (
                "Scatter plot for "
                + self.aggregate_col
                + " "
                + self.aggregate_fn
            )

        self.chart = figure(
            title=self.title,
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

        self.tile_provider = _get_provider(self.tile_provider)
        if self.tile_provider is not None:
            self.chart.add_tile(self.tile_provider)
            self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
            timeout=self.timeout,
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

    def reload_chart(self, data, update_source=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            self.interactive_image.update_chart(data_source=data)
            if update_source:
                self.format_source_data(data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def temp_callback(event):
            xmin, xmax = event.geometry["x0"], event.geometry["x1"]
            ymin, ymax = event.geometry["y0"], event.geometry["y1"]
            callback(xmin, xmax, ymin, ymax)

        self.chart.on_event(events.SelectionGeometry, temp_callback)

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        if self.no_colors_set:
            self.color_palette = properties_dict["chart_color"][
                "color_palette"
            ]
            self.interactive_image.update_chart()
        self.chart.xgrid.grid_line_color = properties_dict["geo_charts_grids"][
            "xgrid"
        ]
        self.chart.ygrid.grid_line_color = properties_dict["geo_charts_grids"][
            "ygrid"
        ]

        # title
        self.chart.title.text_color = properties_dict["title"]["text_color"]
        self.chart.title.text_font = properties_dict["title"]["text_font"]
        self.chart.title.text_font_style = properties_dict["title"][
            "text_font_style"
        ]
        self.chart.title.text_font_size = properties_dict["title"][
            "text_font_size"
        ]

        if self.show_legend():
            self.color_bar.major_label_text_color = properties_dict["title"][
                "text_color"
            ]
            self.color_bar.title_text_color = properties_dict["title"][
                "text_color"
            ]

        # background, border, padding
        self.chart.background_fill_color = properties_dict[
            "background_fill_color"
        ]
        self.chart.border_fill_color = properties_dict["border_fill_color"]
        self.chart.min_border = properties_dict["min_border"]
        self.chart.outline_line_width = properties_dict["outline_line_width"]
        self.chart.outline_line_alpha = properties_dict["outline_line_alpha"]
        self.chart.outline_line_color = properties_dict["outline_line_color"]

        # x axis title
        self.chart.xaxis.major_label_text_color = properties_dict["xaxis"][
            "major_label_text_color"
        ]
        self.chart.xaxis.axis_line_width = properties_dict["xaxis"][
            "axis_line_width"
        ]
        self.chart.xaxis.axis_line_color = properties_dict["xaxis"][
            "axis_line_color"
        ]

        # y axis title
        self.chart.yaxis.major_label_text_color = properties_dict["yaxis"][
            "major_label_text_color"
        ]
        self.chart.yaxis.axis_line_width = properties_dict["yaxis"][
            "axis_line_width"
        ]
        self.chart.yaxis.axis_line_color = properties_dict["yaxis"][
            "axis_line_color"
        ]

        # axis ticks
        self.chart.axis.major_tick_line_color = properties_dict["axis"][
            "major_tick_line_color"
        ]
        self.chart.axis.minor_tick_line_color = properties_dict["axis"][
            "minor_tick_line_color"
        ]
        self.chart.axis.minor_tick_out = properties_dict["axis"][
            "minor_tick_out"
        ]
        self.chart.axis.major_tick_out = properties_dict["axis"][
            "major_tick_out"
        ]
        self.chart.axis.major_tick_in = properties_dict["axis"][
            "major_tick_in"
        ]


class Graph(BaseGraph):
    """
        Description:
    """

    reset_event = events.Reset
    data_y_axis = "node_y"
    data_x_axis = "node_x"
    no_colors_set = False
    image = None
    constant_limit = None
    color_bar = None

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
                self.constant_limit,
                color_bar=self.color_bar,
                update=update,
            )
            if update is False:
                self.chart.add_layout(self.color_bar, self.legend_position)

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

        if self.constant_limit is None or self.node_aggregate_fn == "count":
            self.constant_limit = [
                float(cp.nanmin(agg.data)),
                float(cp.nanmax(agg.data)),
            ]
            self.render_legend()

        span = {"span": self.constant_limit}
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

        return tf.shade(agg, name=name, **cmap)

    def calc_connected_edges(self, nodes, edges):
        """
        calculate directly connected edges
        """
        connected_edges_columns = [self.node_x, self.node_y]
        if self.edge_aggregate_col is not None:
            connected_edges_columns += [self.edge_aggregate_col]

        x1 = (
            edges.merge(nodes, left_on=self.edge_source, right_on=self.node_id)
            .sort_values([self.edge_source, self.edge_target])[
                [self.edge_source, self.edge_target] + connected_edges_columns
            ]
            .reset_index(drop=True)
        )

        x2 = (
            edges.merge(nodes, left_on=self.edge_target, right_on=self.node_id)
            .sort_values([self.edge_source, self.edge_target])[
                [self.edge_source, self.edge_target] + connected_edges_columns
            ]
            .reset_index(drop=True)
        )

        x1 = x1.merge(
            x2, on=[self.edge_source, self.edge_target], suffixes=("", "_y")
        )

        x2 = x1[[i + "_y" for i in connected_edges_columns]].rename(
            columns={i + "_y": i for i in connected_edges_columns}
        )

        x3 = type(nodes)(
            {self.node_x: np.nan, self.node_y: np.nan}, index=x1.index
        )

        self.connected_edges = cudf.concat(
            [x1[connected_edges_columns], x2[connected_edges_columns], x3]
        ).sort_index()

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
            self.calc_connected_edges(self.nodes, self.edges)

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
        ):
            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            if len(self.nodes) > 10_000:
                if self.source is not None:
                    self.source.data = {
                        self.node_x: [],
                        self.node_y: [],
                        self.node_aggregate_col: [],
                        self.node_aggregate_col + "_color": [],
                    }
                np = nodes_plot(cvs, data_source)
                ep = edges_plot(cvs, data_source)
                plot = tf.stack(ep, np, how="over")
            else:
                plot = edges_plot(cvs, data_source)
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
        if self.node_color_palette is None:
            self.no_colors_set = True
            self.node_color_palette = Hot

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
            title=self.title,
            toolbar_location="right",
            tools="pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
            x_range=self.x_range,
            y_range=self.y_range,
            width=self.width,
            height=self.height,
            output_backend="webgl",
        )

        self.tile_provider = _get_provider(self.tile_provider)
        if self.tile_provider is not None:
            self.chart.add_tile(self.tile_provider)
            self.chart.axis.visible = False

        self.chart.add_tools(BoxSelectTool())

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.nodes,
            timeout=self.timeout,
        )

        if len(self.nodes) <= 10_000:
            self.source = ColumnDataSource(
                {
                    self.node_x: self.nodes[self.node_x].to_array(),
                    self.node_y: self.nodes[self.node_y].to_array(),
                    self.node_aggregate_col: self.nodes[
                        self.node_aggregate_col
                    ].to_array(),
                }
            )
            self.compute_colors()
            self.chart.scatter(
                x=self.node_x,
                y=self.node_y,
                source=self.source,
                radius=self.node_point_size,
                fill_alpha=0.6,
                fill_color=self.node_aggregate_col,
                line_color=self.node_aggregate_col,
                line_width=3,
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

    def reload_chart(self, data, update_source=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if update_source:
                self.format_source_data(data)
            # update connected_edges value for datashaded edges
            self.calc_connected_edges(data, self.edges)

            self.interactive_image.update_chart(data_source=data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def temp_callback(event):
            xmin, xmax = event.geometry["x0"], event.geometry["x1"]
            ymin, ymax = event.geometry["y0"], event.geometry["y1"]
            callback(xmin, xmax, ymin, ymax)

        self.chart.on_event(events.SelectionGeometry, temp_callback)

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.
        """
        if self.no_colors_set:
            self.node_color_palette = properties_dict["chart_color"][
                "color_palette"
            ]
            self.interactive_image.update_chart()
        self.chart.xgrid.grid_line_color = properties_dict["geo_charts_grids"][
            "xgrid"
        ]
        self.chart.ygrid.grid_line_color = properties_dict["geo_charts_grids"][
            "ygrid"
        ]

        # title
        self.chart.title.text_color = properties_dict["title"]["text_color"]
        self.chart.title.text_font = properties_dict["title"]["text_font"]
        self.chart.title.text_font_style = properties_dict["title"][
            "text_font_style"
        ]
        self.chart.title.text_font_size = properties_dict["title"][
            "text_font_size"
        ]
        if self.show_legend():
            self.color_bar.major_label_text_color = properties_dict["title"][
                "text_color"
            ]
            self.color_bar.title_text_color = properties_dict["title"][
                "text_color"
            ]

        # background, border, padding
        self.chart.background_fill_color = properties_dict[
            "background_fill_color"
        ]
        self.chart.border_fill_color = properties_dict["border_fill_color"]
        self.chart.min_border = properties_dict["min_border"]
        self.chart.outline_line_width = properties_dict["outline_line_width"]
        self.chart.outline_line_alpha = properties_dict["outline_line_alpha"]
        self.chart.outline_line_color = properties_dict["outline_line_color"]

        # x axis title
        self.chart.xaxis.major_label_text_color = properties_dict["xaxis"][
            "major_label_text_color"
        ]
        self.chart.xaxis.axis_line_width = properties_dict["xaxis"][
            "axis_line_width"
        ]
        self.chart.xaxis.axis_line_color = properties_dict["xaxis"][
            "axis_line_color"
        ]

        # y axis title
        self.chart.yaxis.major_label_text_color = properties_dict["yaxis"][
            "major_label_text_color"
        ]
        self.chart.yaxis.axis_line_width = properties_dict["yaxis"][
            "axis_line_width"
        ]
        self.chart.yaxis.axis_line_color = properties_dict["yaxis"][
            "axis_line_color"
        ]

        # axis ticks
        self.chart.axis.major_tick_line_color = properties_dict["axis"][
            "major_tick_line_color"
        ]
        self.chart.axis.minor_tick_line_color = properties_dict["axis"][
            "minor_tick_line_color"
        ]
        self.chart.axis.minor_tick_out = properties_dict["axis"][
            "minor_tick_out"
        ]
        self.chart.axis.major_tick_out = properties_dict["axis"][
            "major_tick_out"
        ]
        self.chart.axis.major_tick_in = properties_dict["axis"][
            "major_tick_in"
        ]


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

        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            agg = cvs.line(source=data_source, x=self.x, y=self.y)
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
        if self.color is None:
            self.color = "#8735fb"

        if len(self.title) == 0:
            if self.x == self.y:
                self.title = "Line plot for " + self.x
            else:
                self.title = "Line plot for (" + self.x + "," + self.y + ")"

        self.chart = figure(
            title=self.title,
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
        # self.chart.add_tile(self.tile_provider)
        # self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
            timeout=self.timeout,
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

    def reload_chart(self, data, update_source=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            self.interactive_image.update_chart(data_source=data)
            if update_source:
                self.format_source_data(data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def temp_callback(event):
            xmin, xmax = event.geometry["x0"], event.geometry["x1"]
            ymin, ymax = event.geometry["y0"], event.geometry["y1"]
            callback(xmin, xmax, ymin, ymax)

        self.chart.on_event(events.SelectionGeometry, temp_callback)

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        if self.no_color_set:
            self.color = properties_dict["chart_color"]["color"]
            self.interactive_image.update_chart()
        self.chart.xgrid.grid_line_color = properties_dict["geo_charts_grids"][
            "xgrid"
        ]
        self.chart.ygrid.grid_line_color = properties_dict["geo_charts_grids"][
            "ygrid"
        ]

        # title
        self.chart.title.text_color = properties_dict["title"]["text_color"]
        self.chart.title.text_font = properties_dict["title"]["text_font"]
        self.chart.title.text_font_style = properties_dict["title"][
            "text_font_style"
        ]
        self.chart.title.text_font_size = properties_dict["title"][
            "text_font_size"
        ]

        # background, border, padding
        self.chart.background_fill_color = properties_dict[
            "background_fill_color"
        ]
        self.chart.border_fill_color = properties_dict["border_fill_color"]
        self.chart.min_border = properties_dict["min_border"]
        self.chart.outline_line_width = properties_dict["outline_line_width"]
        self.chart.outline_line_alpha = properties_dict["outline_line_alpha"]
        self.chart.outline_line_color = properties_dict["outline_line_color"]

        # x axis title
        self.chart.xaxis.major_label_text_color = properties_dict["xaxis"][
            "major_label_text_color"
        ]
        self.chart.xaxis.axis_line_width = properties_dict["xaxis"][
            "axis_line_width"
        ]
        self.chart.xaxis.axis_line_color = properties_dict["xaxis"][
            "axis_line_color"
        ]

        # y axis title
        self.chart.yaxis.major_label_text_color = properties_dict["yaxis"][
            "major_label_text_color"
        ]
        self.chart.yaxis.axis_line_width = properties_dict["yaxis"][
            "axis_line_width"
        ]
        self.chart.yaxis.axis_line_color = properties_dict["yaxis"][
            "axis_line_color"
        ]

        # axis ticks
        self.chart.axis.major_tick_line_color = properties_dict["axis"][
            "major_tick_line_color"
        ]
        self.chart.axis.minor_tick_line_color = properties_dict["axis"][
            "minor_tick_line_color"
        ]
        self.chart.axis.minor_tick_out = properties_dict["axis"][
            "minor_tick_out"
        ]
        self.chart.axis.major_tick_out = properties_dict["axis"][
            "major_tick_out"
        ]
        self.chart.axis.major_tick_in = properties_dict["axis"][
            "major_tick_in"
        ]


class StackedLines(BaseStackedLine):
    """
        Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    use_data_tiles = False
    no_colors_set = False
    color_bar = None

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

        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = ds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            aggs = dict(
                (_y, cvs.line(data_source, x=self.x, y=_y)) for _y in self.y
            )
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

        if self.colors == []:
            self.no_colors_set = True
            self.colors = ["#8735fb"] * len(self.y)

        if len(self.title) == 0:
            self.title = "Stacked Line plots on x-axis: " + self.x

        self.chart = figure(
            title=self.title,
            toolbar_location="right",
            tools="pan, xwheel_zoom, reset",
            active_scroll="xwheel_zoom",
            active_drag="pan",
            x_range=self.x_range,
            y_range=self.y_range,
            width=self.width,
            height=self.height,
            **self.library_specific_params,
        )

        self.chart.add_tools(BoxSelectTool(dimensions="width"))

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
            self.chart.add_layout(self.color_bar, self.legend_position)

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
            timeout=self.timeout,
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

    def reload_chart(self, data, update_source=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            self.interactive_image.update_chart(data_source=data)
            if update_source:
                self.format_source_data(data)

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def temp_callback(event):
            xmin, xmax = event.geometry["x0"], event.geometry["x1"]
            ymin, ymax = event.geometry["y0"], event.geometry["y1"]
            callback(xmin, xmax, ymin, ymax)

        self.chart.on_event(events.SelectionGeometry, temp_callback)

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        if self.no_colors_set:
            self.colors = [properties_dict["chart_color"]["color"]] * len(
                self.y
            )
            self.interactive_image.update_chart()
        self.chart.xgrid.grid_line_color = properties_dict["geo_charts_grids"][
            "xgrid"
        ]
        self.chart.ygrid.grid_line_color = properties_dict["geo_charts_grids"][
            "ygrid"
        ]

        # title
        self.chart.title.text_color = properties_dict["title"]["text_color"]
        self.chart.title.text_font = properties_dict["title"]["text_font"]
        self.chart.title.text_font_style = properties_dict["title"][
            "text_font_style"
        ]
        self.chart.title.text_font_size = properties_dict["title"][
            "text_font_size"
        ]
        if self.legend:
            self.color_bar.major_label_text_color = properties_dict["title"][
                "text_color"
            ]
            self.color_bar.title_text_color = properties_dict["title"][
                "text_color"
            ]

        # background, border, padding
        self.chart.background_fill_color = properties_dict[
            "background_fill_color"
        ]
        self.chart.border_fill_color = properties_dict["border_fill_color"]
        self.chart.min_border = properties_dict["min_border"]
        self.chart.outline_line_width = properties_dict["outline_line_width"]
        self.chart.outline_line_alpha = properties_dict["outline_line_alpha"]
        self.chart.outline_line_color = properties_dict["outline_line_color"]

        # x axis title
        self.chart.xaxis.major_label_text_color = properties_dict["xaxis"][
            "major_label_text_color"
        ]
        self.chart.xaxis.axis_line_width = properties_dict["xaxis"][
            "axis_line_width"
        ]
        self.chart.xaxis.axis_line_color = properties_dict["xaxis"][
            "axis_line_color"
        ]

        # y axis title
        self.chart.yaxis.major_label_text_color = properties_dict["yaxis"][
            "major_label_text_color"
        ]
        self.chart.yaxis.axis_line_width = properties_dict["yaxis"][
            "axis_line_width"
        ]
        self.chart.yaxis.axis_line_color = properties_dict["yaxis"][
            "axis_line_color"
        ]

        # axis ticks
        self.chart.axis.major_tick_line_color = properties_dict["axis"][
            "major_tick_line_color"
        ]
        self.chart.axis.minor_tick_line_color = properties_dict["axis"][
            "minor_tick_line_color"
        ]
        self.chart.axis.minor_tick_out = properties_dict["axis"][
            "minor_tick_out"
        ]
        self.chart.axis.major_tick_out = properties_dict["axis"][
            "major_tick_out"
        ]
        self.chart.axis.major_tick_in = properties_dict["axis"][
            "major_tick_in"
        ]
