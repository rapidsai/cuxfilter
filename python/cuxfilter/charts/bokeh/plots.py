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

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if self.color is None:
            self.sub_chart.glyph.fill_color = theme.chart_color
            self.sub_chart.glyph.line_color = theme.chart_color

        # interactive slider
        self.datatile_active_color = theme.datatile_active_color


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
            x_range=(
                self.source.data[self.data_x_axis]
                if self.x_dtype == "object"
                else None
            ),
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

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if self.color is None:
            self.sub_chart.glyph.line_color = theme.chart_color

        # interactive slider
        self.datatile_active_color = theme.datatile_active_color
