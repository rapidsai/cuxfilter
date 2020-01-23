from ..core.non_aggregate import (
    BaseScatterGeo,
    BaseScatter,
    BaseLine,
    BaseStackedLine,
)
from .custom_extensions import InteractiveImage

import datashader as cds
from datashader import transfer_functions as tf
from datashader.colors import Hot
import numpy as np
from bokeh import events
from bokeh.plotting import figure
from bokeh.models import BoxSelectTool
from bokeh.tile_providers import get_provider


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


cds.transfer_functions._mask_lookup[
    "rect_vertical"
] = _rect_vertical_mask
cds.transfer_functions._mask_lookup[
    "rect_horizontal"
] = _rect_horizontal_mask


class ScatterGeo(BaseScatterGeo):
    """
        Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    no_colors_set = False

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

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = cds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            agg = cvs.points(
                data_source,
                self.x,
                self.y,
                getattr(cds, self.aggregate_fn)(self.aggregate_col),
            )
            img = tf.shade(
                agg, cmap=self.color_palette, how=self.pixel_shade_type
            )
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

        if type(self.tile_provider) == str:
            self.tile_provider = get_provider(self.tile_provider)

        if "title" in self.library_specific_params:
            self.title = self.library_specific_params["title"]
        else:
            self.title = (
                "Geo Scatter plot for "
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
        self.chart.add_tile(self.tile_provider)
        self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
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
            self.generate_chart()
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


class Scatter(BaseScatter):
    """
        Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    no_colors_set = False

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

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = cds.Canvas(
                plot_width=w, plot_height=h, x_range=x_range, y_range=y_range
            )
            agg = cvs.points(
                data_source,
                self.x,
                self.y,
                getattr(cds, self.aggregate_fn)(self.aggregate_col),
            )
            img = tf.shade(
                agg, cmap=self.color_palette, how=self.pixel_shade_type
            )
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

        if "title" in self.library_specific_params:
            self.title = self.library_specific_params["title"]
        else:
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
        # self.chart.add_tile(self.tile_provider)
        # self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
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
            self.generate_chart()
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

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = cds.Canvas(
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

        if "title" in self.library_specific_params:
            self.title = self.library_specific_params["title"]
        else:
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
            self.generate_chart()
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

    def generate_InteractiveImage_callback(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = cds.Canvas(
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

        if "title" in self.library_specific_params:
            self.title = self.library_specific_params["title"]
        else:
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
        # self.chart.add_tile(self.tile_provider)
        # self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(
            self.chart,
            self.generate_InteractiveImage_callback(),
            data_source=self.source,
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
            self.generate_chart()
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
