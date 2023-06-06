import numpy as np

from ..core_chart import BaseChart
from ....layouts import chart_view
from ....assets import cudf_utils


class BaseNumberChart(BaseChart):
    stride = 1
    # widget is a chart type that can be rendered in a sidebar or main layout
    is_widget = True

    @property
    def use_data_tiles(self):
        return self.expression is None

    @property
    def is_datasize_indicator(self):
        return not (self.x or self.expression)

    @property
    def name(self):
        value = (self.x or self.expression) or ""
        return f"{value}_{self.chart_type}_{self.title}"

    def __init__(
        self,
        x=None,
        expression=None,
        aggregate_fn="count",
        title="",
        widget=True,
        format="{value}",
        colors=[],
        font_size="18pt",
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
        self.x = x
        self.expression = expression
        self.title = title if title else (x or expression)
        self.aggregate_fn = aggregate_fn
        self.format = format
        self.colors = colors
        self.font_size = font_size
        self.library_specific_params = library_specific_params
        self.chart_type = (
            "number_chart" if not widget else "number_chart_widget"
        )

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        if self.is_datasize_indicator:
            # datasize indicator
            self.min_value = 0
            self.max_value = len(dashboard_cls._cuxfilter_df.data)
        elif self.x:
            self.expression = f"data.{self.x}"
        elif self.expression:
            for i in dashboard_cls._cuxfilter_df.data.columns:
                self.expression = self.expression.replace(i, f"data.{i}")

        self.calculate_source(dashboard_cls._cuxfilter_df.data)
        self.generate_chart()

    def view(self):
        return chart_view(self.chart, title=self.title)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        pass

    def reload_chart(self, data, patch_update=True):
        """
        reload chart
        """
        self.calculate_source(data, patch_update=patch_update)

    def _compute_source(self, query, local_dict, indices):
        """
        Compute source dataframe based on the values query and indices.
        If both are not provided, return the original dataframe.
        """
        return cudf_utils.query_df(self.source, query, local_dict, indices)
