import holoviews as hv
import param
import pandas as pd
from cuxfilter.charts.core.aggregate import BaseAggregateChart
from cuxfilter.assets.numba_kernels import calc_groupby
import panel as pn
import cudf


class InteractiveBar(param.Parameterized):
    x = param.String("x", doc="x axis column name")
    y = param.List(["y"], doc="y axis column names as a list")
    source_df = param.ClassSelector(
        class_=(cudf.DataFrame, pd.DataFrame),
        default=cudf.DataFrame(),
        doc="source dataframe",
    )
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
    title = param.String("InteractiveBar", doc="title of the chart")

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
    def bars(self, **kwargs):
        return hv.Bars(
            self.source_df,
            kdims=self.x,
            **{} if self.y is None else {"vdims": self.y},
        )

    def get_base_chart(self):
        return self.bars().opts(alpha=self.unselected_alpha)

    def view(self):
        return (
            (
                self.get_base_chart()
                * hv.DynamicMap(
                    self.bars,
                    streams=[self.box_stream, self.reset_stream],
                ).opts(
                    tools=self.tools,
                    responsive=True,
                    default_tools=[],
                    nonselection_alpha=1,
                    active_tools=["xbox_select"],
                    **self.library_specific_params,
                )
            )
            .relabel(self.title)
            .opts(shared_axes=False)
        )


class Bar(BaseAggregateChart):
    def generate_chart(self, **kwargs):
        """
        generate chart for the x and y columns, and apply aggregate function
        """
        self.chart = InteractiveBar(
            x=self.x,
            y=[self.y] if isinstance(self.y, str) else self.y,
            source_df=self.calculate_source(),
            library_specific_params=self.library_specific_params,
            unselected_alpha=self.unselected_alpha,
            title=self.title,
        )

    def calculate_source(self, data=None):
        """
        Description:
            Calculate the binned counts for the bars for the x column
        -------------------------------------------
        Input:
            data = cudf.DataFrame
        -------------------------------------------
        Output:
            cudf.DataFrame
        """
        data = self.source if data is None else data
        return calc_groupby(self, data)

    def reload_chart(self, data):
        """
        reload chart with new data
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
        apply thematic changes to the chart based on the theme
        """
        if "fill_color" not in self.library_specific_params:
            self.library_specific_params["fill_color"] = theme.chart_color
