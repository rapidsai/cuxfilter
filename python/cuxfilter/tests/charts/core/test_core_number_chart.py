import pytest
import cuxfilter
from cuxfilter.charts.core.aggregate.core_number_chart import BaseNumberChart
from cuxfilter.charts import bar, panel_widgets
from cuxfilter.layouts import chart_view

from ..utils import initialize_df, df_types

df_args = {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
dfs = [initialize_df(type, df_args) for type in df_types]
cux_dfs = [cuxfilter.DataFrame.from_dataframe(df) for df in dfs]


class TestBaseNumberChart:
    _datasize_title = "_datasize_indicator_Datapoints Selected"

    def test_variables(self):
        bnc = BaseNumberChart(title="custom_title")

        # BaseChart variables
        assert bnc.x is None
        assert bnc.expression is None
        assert bnc.title == "custom_title"
        assert bnc.aggregate_fn == "count"
        assert bnc.format == "{value}"
        assert bnc.colors == []
        assert bnc.font_size == "18pt"
        assert bnc.chart_type == "number_chart_widget"
        assert bnc.use_data_tiles is True
        assert bnc._library_specific_params == {}
        assert bnc.is_datasize_indicator is True
        assert bnc.name == "_number_chart_widget_custom_title"

    @pytest.mark.parametrize("cux_df", cux_dfs)
    @pytest.mark.parametrize(
        "x, expression, min_, max_",
        [
            (None, None, 0, 5),  # 0, len(df)
            ("key", None, 0, 0),
            (None, "key+val", 0, 0),
        ],
    )
    def test_initiate_chart(self, cux_df, x, expression, min_, max_):
        bnc = BaseNumberChart(x, expression)
        dashboard = cux_df.dashboard(charts=[])
        bnc.initiate_chart(dashboard)

        assert bnc.min_value == min_
        assert bnc.max_value == max_

    @pytest.mark.parametrize("cux_df", cux_dfs)
    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, cux_df, chart, _chart):
        bnc = BaseNumberChart()
        dashboard = cux_df.dashboard(charts=[])
        bnc.initiate_chart(dashboard)
        bnc.chart = chart
        bnc.title = "title"

        assert str(bnc.view()) == str(chart_view(_chart, title="title"))

    @pytest.mark.parametrize("cux_df", cux_dfs)
    @pytest.mark.parametrize(
        "query_tuple, result", [((1, 4), 4.0), ((0, 4), 5.0), ((1, 1), 1.0)]
    )
    def test_query_chart_by_range(self, cux_df, query_tuple, result):
        active_chart = bar(x="key")
        active_chart.stride = 1
        active_chart.min_value = 0
        dashboard = cux_df.dashboard(charts=[active_chart])
        dashboard._active_view = active_chart
        dashboard._calc_data_tiles()
        bnc = dashboard._sidebar[self._datasize_title]
        datatile = dashboard._data_tiles[self._datasize_title]
        bnc.query_chart_by_range(active_chart, query_tuple, datatile)

        assert result == bnc.chart[0].value

    @pytest.mark.parametrize("cux_df", cux_dfs)
    @pytest.mark.parametrize(
        "old_indices, new_indices, prev_value, result",
        [([], [1], 5.0, 1.0), ([1], [2], 1.0, 1.0), ([2], [2, 4], 1.0, 2.0)],
    )
    def test_query_chart_by_indices(
        self, cux_df, old_indices, new_indices, prev_value, result
    ):
        active_chart = panel_widgets.multi_select("key")
        dashboard = cux_df.dashboard(charts=[active_chart])
        dashboard._active_view = active_chart
        dashboard._calc_data_tiles(cumsum=False)
        bnc = dashboard._sidebar[self._datasize_title]
        bnc.reset_chart(prev_value)

        datatile = dashboard._data_tiles[self._datasize_title]
        bnc.query_chart_by_indices(
            active_chart, old_indices, new_indices, datatile
        )

        assert result == bnc.chart[0].value
