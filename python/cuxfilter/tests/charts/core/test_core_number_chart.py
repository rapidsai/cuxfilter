import pytest
import cuxfilter
from cuxfilter.charts.core.aggregate.core_number_chart import BaseNumberChart
from unittest import mock
from ..utils import initialize_df, df_types

df_args = {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
dfs = [initialize_df(type, df_args) for type in df_types]
cux_dfs = [cuxfilter.DataFrame.from_dataframe(df) for df in dfs]


class TestBaseNumberChart:
    _datasize_title = "_datasize_indicator_Datapoints Selected"

    def test_variables(self):
        bnc = BaseNumberChart(title="custom_title")

        # BaseChart variables
        assert bnc.expression is None
        assert bnc.title == "custom_title"
        assert bnc.aggregate_fn == "count"
        assert bnc.format == "{value}"
        assert bnc.colors == []
        assert bnc.font_size == "18pt"
        assert bnc.chart_type == "base_number_chart"
        assert bnc._library_specific_params == {}
        assert bnc.is_datasize_indicator is False
        assert bnc.name == "base_number_chart_custom_title"

    @pytest.mark.parametrize("cux_df", cux_dfs)
    def test_initiate_chart(self, cux_df, expression="key"):
        with mock.patch.object(
            BaseNumberChart, "generate_chart"
        ) as mock_generate_chart:
            # Initialize a BaseNumberChart instance and call initiate_chart
            bnc = BaseNumberChart(x="x", y="y", title="Test Chart")
            dashboard = cux_df.dashboard(charts=[])
            bnc.initiate_chart(dashboard)

            # Assert that the generate_chart method was called once
            mock_generate_chart.assert_called_once()

    @pytest.mark.parametrize("cux_df", cux_dfs)
    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, cux_df, chart, _chart):
        bnc = BaseNumberChart()
        dashboard = cux_df.dashboard(charts=[])
        bnc.initiate_chart(dashboard)
        bnc.chart = chart
        bnc.title = "title"

        assert bnc.view() == _chart
