from ..core.aggregate import BaseBar, BaseChoropleth, BaseLine

import pandas as pd
import numpy as np
from typing import Type
from bokeh import events
from bokeh.plotting import figure
import bokeh
from bokeh.models import (
    ColumnDataSource,
    LinearColorMapper,
    ColorBar,
    BasicTicker,
    PrintfTickFormatter,
)


class Bar(BaseBar):
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
        range_x_origin = [round(x, 4) for x in source_dict["X"]]
        range_x = []

        if self.max_value < 1:
            """
            handling labels in bokeh plots when max value is under 1
            """
            range_x = [int(x * 100) for x in range_x_origin]
            if self.x_label_map is None:
                temp_mapper_index = list(
                    range(
                        int(round(self.min_value)),
                        int(round(self.max_value)) * 100 + 1,
                    )
                )
                temp_mapper_value = [str(x / 100) for x in temp_mapper_index]
                self.x_label_map = dict(
                    zip(temp_mapper_index, temp_mapper_value)
                )
        else:
            range_x = range_x_origin

        if patch_update is False:
            self.source = ColumnDataSource(
                dict(x=np.array(range_x), top=np.array(source_dict["Y"]))
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
        if "title" in self.library_specific_params:
            self.title = self.library_specific_params["title"]
        else:
            self.title = self.x

        self.chart = figure(
            title=self.title,
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
            )
        else:
            self.sub_chart = self.chart.vbar(
                x=self.data_x_axis,
                top=self.data_y_axis,
                width=0.9,
                source=self.source,
                color=self.color,
            )
        self.chart.xaxis.axis_label = self.x
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


class Line(BaseLine):
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
        range_x_origin = [round(x, 4) for x in source_dict["X"]]
        range_x = []

        if self.max_value < 1:
            """
            handling labels in bokeh plots when max value is under 1
            """
            range_x = [int(x * 100) for x in range_x_origin]
            if self.x_label_map is None:
                temp_mapper_index = list(
                    range(
                        int(round(self.min_value)),
                        int(round(self.max_value)) * 100 + 1,
                    )
                )
                temp_mapper_value = [str(x / 100) for x in temp_mapper_index]
                self.x_label_map = dict(
                    zip(temp_mapper_index, temp_mapper_value)
                )
        else:
            range_x = range_x_origin

        if patch_update is False:
            self.source = ColumnDataSource(
                dict(x=np.array(range_x), y=np.array(source_dict["Y"]))
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
        if "title" in self.library_specific_params:
            self.title = self.library_specific_params["title"]
        else:
            self.title = self.x

        self.chart = figure(
            title=self.title,
            tools=" pan, wheel_zoom, reset",
            active_scroll="wheel_zoom",
            active_drag="pan",
        )
        if self.color is None:
            self.sub_chart = self.chart.line(
                x=self.data_x_axis, y=self.data_y_axis, source=self.source
            )
        else:
            self.sub_chart = self.chart.line(
                x=self.data_x_axis,
                y=self.data_y_axis,
                source=self.source,
                color=self.color,
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