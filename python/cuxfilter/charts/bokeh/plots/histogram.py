# SPDX-FileCopyrightText: Copyright (c) 2023-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import holoviews as hv
import panel as pn
import param

from cuxfilter.assets.numba_kernels import calc_value_counts
from cuxfilter.charts.core.aggregate import BaseAggregateChart


class InteractiveHistogram(param.Parameterized):
    x = param.String("x", doc="x axis column name")
    source_df = param.Tuple(doc="source dataframe")
    box_stream = param.ClassSelector(
        class_=hv.streams.SelectionXY, default=hv.streams.SelectionXY()
    )
    reset_stream = param.ClassSelector(
        class_=hv.streams.PlotReset,
        default=hv.streams.PlotReset(resetting=False),
    )
    tools = param.List(
        default=[
            "pan",
            "reset",
            "xbox_select",
            "wheel_zoom",
            "save",
        ],
        doc="interactive tools to add to the chart",
    )
    unselected_alpha = param.Number(
        0.2,
        bounds=(0, 1),
        doc=("Transparency of the unselected points. "),
    )
    bounds = param.ClassSelector(
        class_=hv.DynamicMap,
        doc="bounds of the box select tool",
    )
    title = param.String("InteractiveBar", doc="title of the chart")

    library_specific_params = param.Dict({}, doc="library specific params")

    def __init__(self, **params):
        """
        initialize InteractiveHistogram object
        """
        super(InteractiveHistogram, self).__init__(**params)

    def add_box_select_callback(self, callback_fn):
        self.box_stream = hv.streams.SelectionXY(subscribers=[callback_fn])

    def add_reset_callback(self, callback_fn):
        self.reset_stream = hv.streams.PlotReset(subscribers=[callback_fn])

    def update_data(self, data):
        self.source_df = data

    @param.depends("source_df")
    def histogram(self, **kwargs):
        chart_module = hv.Histogram
        if self.source_df[0].dtype == "object":
            chart_module = hv.Bars
        return chart_module(self.source_df, kdims=self.x)

    def get_base_chart(self):
        return self.histogram().opts(alpha=self.unselected_alpha)

    def view(self):
        return (
            (
                self.get_base_chart()
                * hv.DynamicMap(
                    self.histogram,
                    streams=[self.box_stream, self.reset_stream],
                ).opts(
                    tools=self.tools,
                    responsive=True,
                    active_tools=["xbox_select"],
                    nonselection_alpha=1,
                    ylabel="frequency",
                    **self.library_specific_params,
                )
            )
            .relabel(self.title)
            .opts(shared_axes=False)
        )


class Histogram(BaseAggregateChart):
    def generate_chart(self, **kwargs):
        self.chart = InteractiveHistogram(
            x=self.x,
            source_df=self.calculate_source(),
            unselected_alpha=self.unselected_alpha,
            library_specific_params=self.library_specific_params,
            title=self.title,
        )

    def calculate_source(self, data=None):
        """
        Calculate the binned counts for the histogram for the x column.

        Parameters
        ----------
        data : cudf.DataFrame, optional
            Input dataframe. If None, uses self.source.

        Returns
        -------
        cudf.DataFrame
            DataFrame with binned counts for the x column.
        """
        data = self.source if data is None else data
        return calc_value_counts(
            data[self.x],
            self.stride,
            self.min_value,
            self.custom_binning,
        )

    def reload_chart(self, data):
        """
        Reload chart with new data
        """
        self.chart.update_data(self.calculate_source(data))

    def view(self, width=800, height=400):
        return pn.panel(
            self.chart.view().opts(
                width=width, height=height, responsive=False
            )
        )

    def apply_theme(self, theme):
        """
        Apply thematic changes to the chart based on the theme
        """
        if "fill_color" not in self.library_specific_params:
            self.library_specific_params["fill_color"] = theme.chart_color
