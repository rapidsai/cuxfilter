import cupy as cp
import holoviews as hv
import param
from cuxfilter.charts.core.aggregate import BaseAggregateChart
from cuxfilter.layouts import chart_view
from cuxfilter.assets.numba_kernels import calc_groupby
import panel as pn


class InteractiveBar(param.Parameterized):
    x = param.String("x", doc="x axis column name")
    y = param.List(["y"], doc="y axis column names as a list")
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
            "xbox_select",
            "reset",
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

    library_specific_params = param.Dict({}, doc="library specific params")

    def __init__(self, **params):
        """
        initialize InteractiveBar object
        """
        super(InteractiveBar, self).__init__(**params)

    def add_box_select_callback(self, callback_fn):
        self.box_stream = hv.streams.SelectionXY(subscribers=[callback_fn])

    def add_reset_callback(self, callback_fn):
        self.reset_stream = hv.streams.PlotReset(subscribers=[callback_fn])

    def update_data(self, data):
        self.source_df = data

    @param.depends("source_df")
    def histogram(self, **kwargs):
        return hv.Bars(
            self.source_df,
            kdims=self.x,
            vdims=self.y,
        ).opts(
            tools=self.tools,
            responsive=True,
            default_tools=[],
            nonselection_alpha=0.1,
            active_tools=["xbox_select"],
            **self.library_specific_params,
        )

    def get_base_chart(self):
        return self.histogram()

    def view(self):
        histogram = self.histogram().opts(alpha=0)
        box = hv.streams.BoundsXY(source=histogram, bounds=(0, 0, 0, 0))
        bounds = hv.DynamicMap(lambda bounds: hv.Bounds(bounds), streams=[box])
        return (
            histogram
            * hv.DynamicMap(
                self.histogram,
                streams=[self.box_stream, self.reset_stream],
            )
        ).opts(shared_axes=False) * bounds


class Bar(BaseAggregateChart):
    @param.depends("source")
    def generate_chart(self, **kwargs):
        """
        generate chart for the x and y columns, and apply aggregate function
        """
        self.chart = InteractiveBar(
            x=self.x,
            y=[self.y] if isinstance(self.y, str) else self.y,
            source_df=self.calculate_source(),
            library_specific_params=self.library_specific_params,
            unselected_alpha=0.1,
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
        return calc_groupby(self, data)

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
            self.chart.view(),
            title=self.title,
        )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if "color" not in self.library_specific_params:
            self.library_specific_params["color"] = theme.chart_color
