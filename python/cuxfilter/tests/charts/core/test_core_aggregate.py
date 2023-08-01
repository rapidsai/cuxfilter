import pytest
from bokeh.events import ButtonClick
import panel as pn

from cuxfilter.charts.core.aggregate.core_aggregate import BaseAggregateChart
import cuxfilter

from ..utils import initialize_df, df_types

df_args = {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
dfs = [initialize_df(type, df_args) for type in df_types]
cux_dfs = [cuxfilter.DataFrame.from_dataframe(df) for df in dfs]
# create cudf and dask_cudf backed cuxfilter dataframes
dashboards = [
    cux_df.dashboard(charts=[], title="test_title") for cux_df in cux_dfs
]


class TestBaseAggregateChart:
    def test_variables(self):
        bb = BaseAggregateChart(x="test_x")

        assert bb.chart_type is None
        assert bb.reset_event is None
        assert bb.filter_widget is None
        assert bb.use_data_tiles is True
        assert bb.x == "test_x"
        assert bb.y is None
        assert bb.data_points is None
        assert bb.add_interaction is True
        assert bb.aggregate_fn == "count"
        assert bb.width == 400
        assert bb.height == 400
        assert bb.stride is None
        assert bb.stride_type == int
        assert bb.library_specific_params == {}

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_initiate_chart(self, dashboard):
        bb = BaseAggregateChart(x="key")
        bb.initiate_chart(dashboard)

        assert bb.min_value == 0.0
        assert bb.max_value == 4.0
        assert bb.data_points == 5
        assert bb.stride == 1
        assert bb.stride_type == int

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bnac = BaseAggregateChart(x="test_x", add_interaction=False)
        bnac.chart = chart
        bnac.width = 400

        assert str(bnac.view()) == str(
            pn.panel(_chart, width=bnac.width, title=bnac.title)
        )

    @pytest.mark.parametrize("dashboard", dashboards)
    @pytest.mark.parametrize("df", dfs)
    @pytest.mark.parametrize(
        "bb, result",
        [
            (
                BaseAggregateChart(x="key", y="val"),
                {
                    "X": [0.0, 1.0, 2.0, 3.0, 4.0],
                    "Y": [10.0, 11.0, 12.0, 13.0, 14.0],
                },
            ),
            (
                BaseAggregateChart(x="key"),
                {
                    "X": [0.0, 1.0, 2.0, 3.0, 4.0],
                    "Y": [1.0, 1.0, 1.0, 1.0, 1.0],
                },
            ),
        ],
    )
    def test_calculate_source(self, dashboard, df, bb, result):
        bb.initiate_chart(dashboard)
        self.result = None

        def func1(dict_temp, patch_update=False):
            self.result = dict_temp

        bb.format_source_data = func1
        bb.calculate_source(df)
        assert all(result["X"] == self.result["X"])
        assert all(result["Y"] == self.result["Y"])

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_add_range_slider_filter(self, dashboard):
        bb = BaseAggregateChart(x="key")
        bb.chart_type = "bar"
        dashboard.add_charts([bb])
        assert isinstance(bb.filter_widget, pn.widgets.RangeSlider)
        assert bb.filter_widget.value == (0, 4)

    @pytest.mark.parametrize("dashboard", dashboards)
    @pytest.mark.parametrize(
        "range, query, local_dict",
        [
            (
                (3, 4),
                "@key_min <= key <= @key_max",
                {"key_min": 3, "key_max": 4},
            ),
            (
                (0, 0),
                "@key_min <= key <= @key_max",
                {"key_min": 0, "key_max": 0},
            ),
        ],
    )
    def test_compute_query_dict(self, dashboard, range, query, local_dict):
        bb = BaseAggregateChart(x="key")
        bb.chart_type = "bar"
        dashboard.add_charts([bb])
        bb.filter_widget.value = range
        # test the following function behavior
        bb.compute_query_dict(
            dashboard._query_str_dict,
            dashboard._query_local_variables_dict,
        )

        assert dashboard._query_str_dict[f"key_count_bar_{bb.title}"] == query
        for key in local_dict:
            assert (
                dashboard._query_local_variables_dict[key] == local_dict[key]
            )

    @pytest.mark.parametrize("dashboard", dashboards)
    @pytest.mark.parametrize(
        "event, result", [(None, None), (ButtonClick, "func_Called")]
    )
    def test_add_events(self, dashboard, event, result):
        bb = BaseAggregateChart(x="key")
        self.result = None

        def test_func(cls):
            self.result = "func_Called"

        bb.add_reset_event = test_func
        bb.reset_event = event
        # test the following function behavior
        bb.add_events(dashboard)

        assert self.result == result

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_add_reset_event(self, dashboard):
        bb = BaseAggregateChart(x="key")
        self.result = None

        def test_func(event, callback):
            self.result = callback

        class chart:
            on_event = test_func

        bb.chart = chart
        # test the following function behavior
        bb.add_reset_event(dashboard)
        assert self.result.__name__ == "reset_callback"

    def test_label_mappers(self):
        bac = BaseAggregateChart(x="test_x")
        library_specific_params = {
            "x_label_map": {"a": 1, "b": 2},
            "y_label_map": {"a": 1, "b": 2},
        }
        bac.library_specific_params = library_specific_params

        assert bac.x_label_map == {"a": 1, "b": 2}
        assert bac.y_label_map == {"a": 1, "b": 2}
