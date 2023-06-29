import numpy as np
import holoviews as hv
import param
from cuxfilter.charts.core.aggregate import BaseAggregateChart
from cuxfilter.layouts import chart_view
from cuxfilter.assets.numba_kernels import calc_value_counts
import panel as pn
import cudf
import dask_cudf


class InteractiveHistogram(param.Parameterized):
    x = param.String("x", doc="x axis column name")
    source_df = param.Tuple(doc="source dataFrame")
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
        return chart_module(self.source_df, kdims=self.x).opts(
            tools=self.tools,
            responsive=True,
            active_tools=["box_select"],
            nonselection_alpha=0.1,
            ylabel="frequency",
            **self.library_specific_params,
        )

    def view(self):
        histogram = self.histogram().opts(alpha=0.1)
        box = hv.streams.BoundsXY(source=histogram, bounds=(0, 0, 0, 0))
        bounds = hv.DynamicMap(lambda bounds: hv.Bounds(bounds), streams=[box])
        return (
            histogram
            * hv.DynamicMap(
                self.histogram,
                streams=[self.box_stream, self.reset_stream],
            )
        ).opts(shared_axes=False) * bounds


class Histogram(BaseAggregateChart):
    """
    Description:
    """

    def generate_chart(self, **kwargs):
        """
        returns a histogram chart
        """
        self.chart = InteractiveHistogram(
            x=self.x,
            source_df=self.calculate_source(),
            unselected_alpha=0.1,
            library_specific_params=self.library_specific_params,
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
        self.chart.update_data(self.calculate_source(data))

    def view(self):
        return chart_view(
            # self.generate_chart().opts(  # non-selection alpha is set to 0.1
            #     alpha=0.1,
            # )*
            self.chart.view(),
            title=self.title,
        )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if "color" not in self.library_specific_params:
            self.library_specific_params["color"] = theme.chart_color
