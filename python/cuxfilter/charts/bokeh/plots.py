from ..core.aggregate import BaseAggregateChart

import numpy as np
from bokeh import events
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource


class Bar(BaseAggregateChart):
    """
        Description:
    """

    reset_event = events.Reset
    data_y_axis = "top"
    data_x_axis = "x"

    def format_source_data(self, source_dict, patch_update=False):
        """
        format source

        Parameters:
        -----------
        source_dict: {'X': [], 'Y': []}
        """
        if patch_update is False:
            self.source = ColumnDataSource(
                {
                    self.data_x_axis: np.array(source_dict["X"]),
                    self.data_y_axis: np.array(source_dict["Y"]),
                }
            )
            self.source_backup = self.source.to_df()
        else:
            patch_dict = {
                self.data_y_axis: [
                    (slice(len(source_dict["Y"])), np.array(source_dict["Y"]))
                ]
            }
            self.source.patch(patch_dict)

    def get_source_y_axis(self):
        """
        get y axis column value
        """
        if self.source is not None:
            return self.source.data[self.data_y_axis]
        return self.source

    def generate_chart(self):
        """
        generate chart
        """
        self.chart = figure(
            title=self.title,
            x_range=(
                self.source.data[self.data_x_axis]
                if self.x_dtype == "object"
                else None
            ),
            tools="pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
        )
        if self.color is None:
            self.sub_chart = self.chart.vbar(
                x=self.data_x_axis,
                top=self.data_y_axis,
                width=0.9,
                source=self.source,
                **self.library_specific_params,
            )
        else:
            self.sub_chart = self.chart.vbar(
                x=self.data_x_axis,
                top=self.data_y_axis,
                width=0.9,
                source=self.source,
                color=self.color,
                **self.library_specific_params,
            )
        self.chart.xaxis.axis_label = self.x
        if self.x_axis_tick_formatter:
            self.chart.xaxis.formatter = self.x_axis_tick_formatter
        if self.y_axis_tick_formatter:
            self.chart.yaxis.formatter = self.y_axis_tick_formatter
        if self.autoscaling is False:
            self.chart.y_range.end = self.source.data[self.data_y_axis].max()

        if self.y != self.x:
            self.chart.yaxis.axis_label = self.y
        else:
            self.chart.yaxis.axis_label = self.aggregate_fn

    def update_dimensions(self, width=None, height=None):
        """
        update dimensions
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def apply_mappers(self):
        """
        apply dict mappers to x and y axes if provided
        """
        if self.x_label_map is not None:
            self.chart.xaxis.major_label_overrides = self.x_label_map
        if self.y_label_map is not None:
            self.chart.yaxis.major_label_overrides = self.y_label_map

    def reload_chart(self, data, patch_update=True):
        """
        reload chart
        """
        self.calculate_source(data, patch_update=patch_update)

    def reset_chart(self, data: np.array = np.array([])):
        """
        if len(data) is 0, reset the chart using self.source_backup

        Parmeters:
        ----------
        data = list() --> update self.data_y_axis in self.source
        """
        if data.size == 0:
            data = self.source_backup[self.data_y_axis]

        # verifying length is same as x axis
        x_axis_len = self.source.data[self.data_x_axis].size
        data = data[:x_axis_len]

        patch_dict = {self.data_y_axis: [(slice(data.size), data)]}
        self.source.patch(patch_dict)

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.
        """
        if self.color is None:
            self.sub_chart.glyph.fill_color = properties_dict["chart_color"][
                "color"
            ]
            self.sub_chart.glyph.line_color = properties_dict["chart_color"][
                "color"
            ]

        self.chart.xgrid.grid_line_color = properties_dict["agg_charts_grids"][
            "xgrid"
        ]
        self.chart.ygrid.grid_line_color = properties_dict["agg_charts_grids"][
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
        self.chart.xaxis.axis_label_text_font_style = properties_dict["xaxis"][
            "axis_label_text_font_style"
        ]
        self.chart.xaxis.axis_label_text_color = properties_dict["xaxis"][
            "axis_label_text_color"
        ]
        self.chart.xaxis.axis_label_standoff = properties_dict["xaxis"][
            "axis_label_standoff"
        ]
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
        self.chart.yaxis.axis_label_text_font_style = properties_dict["yaxis"][
            "axis_label_text_font_style"
        ]
        self.chart.yaxis.axis_label_text_color = properties_dict["yaxis"][
            "axis_label_text_color"
        ]
        self.chart.yaxis.axis_label_standoff = properties_dict["yaxis"][
            "axis_label_standoff"
        ]
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

        # interactive slider
        self.datatile_active_color = properties_dict["widgets"][
            "datatile_active_color"
        ]


class Line(BaseAggregateChart):
    """
        Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"

    def format_source_data(self, source_dict, patch_update=False):
        """
        format source

        Parameters:
        -----------
        source_dict: {'X': [], 'Y': []}
        """
        if patch_update is False:
            self.source = ColumnDataSource(
                {
                    self.data_x_axis: np.array(source_dict["X"]),
                    self.data_y_axis: np.array(source_dict["Y"]),
                }
            )
            self.source_backup = self.source.to_df()
        else:
            patch_dict = {
                self.data_y_axis: [
                    (slice(len(source_dict["Y"])), np.array(source_dict["Y"]))
                ]
            }
            self.source.patch(patch_dict)

    def get_source_y_axis(self):
        """
        get y axis column value
        """
        if self.source is not None:
            return self.source.data[self.data_y_axis]
        return self.source

    def generate_chart(self):
        """
        generate chart
        """
        self.chart = figure(
            title=self.title,
            tools="pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
        )
        if self.x_axis_tick_formatter:
            self.chart.xaxis.formatter = self.x_axis_tick_formatter
        if self.y_axis_tick_formatter:
            self.chart.yaxis.formatter = self.y_axis_tick_formatter
        if self.autoscaling is False:
            self.chart.y_range.end = self.source.data[self.data_y_axis].max()

        if self.color is None:
            self.sub_chart = self.chart.line(
                x=self.data_x_axis,
                y=self.data_y_axis,
                source=self.source,
                **self.library_specific_params,
            )
        else:
            self.sub_chart = self.chart.line(
                x=self.data_x_axis,
                y=self.data_y_axis,
                source=self.source,
                color=self.color,
                **self.library_specific_params,
            )

    def update_dimensions(self, width=None, height=None):
        """
        update dimensions
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def apply_mappers(self):
        """
        apply dict mappers to x and y axes if provided
        """
        if self.x_label_map is not None:
            self.chart.xaxis.major_label_overrides = self.x_label_map
        if self.y_label_map is not None:
            self.chart.yaxis.major_label_overrides = self.y_label_map

    def reload_chart(self, data, patch_update=True):
        """
        reload chart
        """
        self.calculate_source(data, patch_update=patch_update)

    def reset_chart(self, data: np.array = np.array([])):
        """
        if len(data) is 0, reset the chart using self.source_backup.

        Parameters:
        -----------
        data = list() --> update self.data_y_axis in self.source
        """
        if data.size == 0:
            data = self.source_backup[self.data_y_axis]

        # verifying length is same as x axis
        x_axis_len = self.source.data[self.data_x_axis].size
        data = data[:x_axis_len]

        patch_dict = {self.data_y_axis: [(slice(data.size), data)]}
        self.source.patch(patch_dict)

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        if self.color is None:
            self.sub_chart.glyph.line_color = properties_dict["chart_color"][
                "color"
            ]

        self.chart.xgrid.grid_line_color = properties_dict["agg_charts_grids"][
            "xgrid"
        ]
        self.chart.ygrid.grid_line_color = properties_dict["agg_charts_grids"][
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
        self.chart.xaxis.axis_label_text_font_style = properties_dict["xaxis"][
            "axis_label_text_font_style"
        ]
        self.chart.xaxis.axis_label_text_color = properties_dict["xaxis"][
            "axis_label_text_color"
        ]
        self.chart.xaxis.axis_label_standoff = properties_dict["xaxis"][
            "axis_label_standoff"
        ]
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
        self.chart.yaxis.axis_label_text_font_style = properties_dict["yaxis"][
            "axis_label_text_font_style"
        ]
        self.chart.yaxis.axis_label_text_color = properties_dict["yaxis"][
            "axis_label_text_color"
        ]
        self.chart.yaxis.axis_label_standoff = properties_dict["yaxis"][
            "axis_label_standoff"
        ]
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

        # interactive slider
        self.datatile_active_color = properties_dict["widgets"][
            "datatile_active_color"
        ]
