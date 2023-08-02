from cuxfilter.charts.core import BaseChart
from cuxfilter.assets import cudf_utils


class BaseNumberChart(BaseChart):
    stride = 1
    # widget is a chart type that can be rendered in a sidebar or main layout
    is_widget = True

    @property
    def is_datasize_indicator(self):
        return False

    def __init__(
        self,
        expression=None,
        aggregate_fn="count",
        title="",
        widget=True,
        format="{value}",
        default_color="black",
        colors=[],
        font_size="18pt",
        title_size="9.75pt",
        **library_specific_params,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.expression = expression
        self.title = title if title else (x or expression)
        self.aggregate_fn = aggregate_fn
        self.format = format
        self.default_color = default_color
        self.colors = colors
        self.font_size = font_size
        self.title_size = title_size
        self.library_specific_params = library_specific_params
        self.chart_type = "base_number_chart"

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        self.generate_chart(dashboard_cls._cuxfilter_df.data)

    def view(self):
        return self.chart

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        pass

    def reload_chart(self, data):
        """
        reload chart
        """
        pass

    def _compute_source(self, query, local_dict, indices):
        """
        Compute source dataframe based on the values query and indices.
        If both are not provided, return the original dataframe.
        """
        return cudf_utils.query_df(self.source, query, local_dict, indices)
