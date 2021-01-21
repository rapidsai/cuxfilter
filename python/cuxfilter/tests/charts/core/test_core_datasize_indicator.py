import pytest
import pandas as pd
import cudf

import cuxfilter
from cuxfilter.charts.core.aggregate.core_datasize_indicator import (
    BaseDataSizeIndicator,
)
from cuxfilter.charts import bar
from cuxfilter.layouts import chart_view


class TestBaseDataSizeIndicator:

    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)

    def test_variables(self):
        bdsi = BaseDataSizeIndicator()

        # BaseChart variables
        assert bdsi.x == ""
        assert bdsi.height == 400
        assert bdsi.width == 400
        assert bdsi._library_specific_params == {}
        assert bdsi.chart_type is None
        assert bdsi.use_data_tiles is True

    def test_initiate_chart(self):
        bdsi = BaseDataSizeIndicator()
        dashboard = self.cux_df.dashboard(charts=[])
        bdsi.initiate_chart(dashboard)

        assert bdsi.min_value == 0
        assert bdsi.max_value == self.df.shape[0]

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bdsi = BaseDataSizeIndicator()
        dashboard = self.cux_df.dashboard(charts=[])
        bdsi.initiate_chart(dashboard)
        bdsi.chart = chart

        assert str(bdsi.view()) == str(
            chart_view(
                _chart,
                css_classes=["non-handle-temp"],
                title="Datapoints Selected",
            )
        )

    def test_calculate_source(self):
        bdsi = BaseDataSizeIndicator()
        dashboard = self.cux_df.dashboard(charts=[])
        bdsi.initiate_chart(dashboard)
        self.result = None

        def func1(dict_temp, patch_update=False):
            self.result = dict_temp

        bdsi.format_source_data = func1
        bdsi.calculate_source(self.df)

        assert self.result == {"X": [1], "Y": [self.df.shape[0]]}

    @pytest.mark.parametrize(
        "query_tuple, result", [((1, 4), 4.0), ((0, 4), 5.0), ((1, 1), 1.0)]
    )
    def test_query_chart_by_range(self, query_tuple, result):
        dashboard = self.cux_df.dashboard(charts=[])
        active_chart = bar(x="key")
        active_chart.stride = 1
        active_chart.min_value = 0
        bdsi = dashboard._charts["_datasize_indicator"]
        self.result = ""

        def reset_chart(datatile_result):
            self.result = datatile_result

        bdsi.reset_chart = reset_chart
        datatile = pd.DataFrame({0: {0: 1.0, 1: 2.0, 2: 3.0, 3: 4.0, 4: 5.0}})
        bdsi.query_chart_by_range(active_chart, query_tuple, datatile)

        assert result == self.result

    @pytest.mark.parametrize(
        "old_indices, new_indices, prev_value, result",
        [([], [1], 5.0, 1.0), ([1], [2], 1.0, 1.0), ([2], [2, 4], 1.0, 2.0)],
    )
    def test_query_chart_by_indices(
        self, old_indices, new_indices, prev_value, result
    ):
        active_chart = bar(x="key")
        active_chart.stride = 1
        active_chart.min_value = 0
        self.result = ""
        dashboard = self.cux_df.dashboard(charts=[active_chart])
        dashboard._active_view = active_chart.name
        dashboard._calc_data_tiles(cumsum=False)
        bdsi = dashboard._charts["_datasize_indicator"]
        bdsi.chart.value = prev_value

        def reset_chart(datatile_result):
            self.result = datatile_result

        bdsi.reset_chart = reset_chart
        datatile = pd.DataFrame({0: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0}})
        bdsi.query_chart_by_indices(
            active_chart, old_indices, new_indices, datatile
        )

        assert result == self.result
