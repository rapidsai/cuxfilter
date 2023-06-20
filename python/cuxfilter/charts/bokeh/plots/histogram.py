import numpy as np
import holoviews as hv
import param
from cuxfilter.charts.core.aggregate import BaseAggregateChart
from cuxfilter.layouts import chart_view
from cuxfilter.assets.numba_kernels import calc_value_counts
import panel as pn


class Histogram(BaseAggregateChart):
    """
    Description:
    """

    def generate_chart(self, **kwargs):
        """
        returns a histogram chart
        """
        chart_module = hv.Histogram
        if self.x_dtype == "object":
            chart_module = hv.Bars
        return chart_module(self.calculate_source(), kdims=self.x).opts(
            tools=[
                "pan",
                "reset",
                "wheel_zoom",
                "save",
                "xbox_select",
            ],
            responsive=True,
            default_tools=[],
            active_tools=["xbox_select"],
            ylabel="frequency",
            **self.library_specific_params,
        )

    def calculate_source(self, data=None):
        """
        Description:
            Calculate the binned counts for the histogram for the x column
        -------------------------------------------
        Input:
            data = cudf.DataFrame
        -------------------------------------------
        Output:
            cudf.DataFrame
        """
        data = data or self.source
        return calc_value_counts(
            data[self.x],
            self.stride,
            self.min_value,
            self.custom_binning,
        )

    def reload_chart(self, data):
        """
        reload chart with new data
        """
        self.source = data

    def view(self):
        return chart_view(
            # self.generate_chart().opts(  # non-selection alpha is set to 0.1
            #     alpha=0.1,
            # )*
            hv.DynamicMap(
                self.generate_chart,
                streams=[self.box_stream, self.reset_stream],
            ),
            title=self.title,
        )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if "color" not in self.library_specific_params:
            self.library_specific_params["color"] = theme.chart_color
