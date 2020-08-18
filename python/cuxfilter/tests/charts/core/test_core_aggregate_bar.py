import pytest
import cudf
from bokeh.events import ButtonClick
import panel as pn

from cuxfilter.charts.core.aggregate.core_aggregate_bar import BaseBar
import cuxfilter
from cuxfilter.layouts import chart_view


class TestBaseBar:

    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title="test_title")

    def test_variables(self):
        bb = BaseBar(x="test_x")

        assert bb.chart_type is None
        assert bb.reset_event is None
        assert bb._datatile_loaded_state is False
        assert bb.filter_widget is None
        assert bb.use_data_tiles is True
        assert bb.datatile_active_color == "#8ab4f7"
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

    def test_initiate_chart(self):
        bb = BaseBar(x="key")
        bb.initiate_chart(self.dashboard)

        assert bb.min_value == 0.0
        assert bb.max_value == 4.0
        assert bb.data_points == 5
        assert bb.stride == 1
        assert bb.stride_type == int

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bnac = BaseBar(x="test_x")
        bnac.chart = chart
        bnac.width = 400

        assert str(bnac.view()) == str(chart_view(_chart, width=bnac.width))

    @pytest.mark.parametrize(
        "bb, result",
        [
            (
                BaseBar(x="key", y="val"),
                {
                    "X": [0.0, 1.0, 2.0, 3.0, 4.0],
                    "Y": [10.0, 11.0, 12.0, 13.0, 14.0],
                },
            ),
            (
                BaseBar(x="key"),
                {
                    "X": [0.0, 1.0, 2.0, 3.0, 4.0],
                    "Y": [1.0, 1.0, 1.0, 1.0, 1.0],
                },
            ),
        ],
    )
    def test_calculate_source(self, bb, result):
        bb.initiate_chart(self.dashboard)
        self.result = None

        def func1(dict_temp, patch_update=False):
            self.result = dict_temp

        bb.format_source_data = func1
        bb.calculate_source(self.df)
        assert all(result["X"] == self.result["X"])
        assert all(result["Y"] == self.result["Y"])

    def test_add_range_slider_filter(self):
        bb = BaseBar(x="key")
        bb.chart_type = "bar"
        self.dashboard.add_charts([bb])
        assert type(bb.filter_widget) == pn.widgets.RangeSlider
        assert bb.filter_widget.value == (0, 4)

    @pytest.mark.parametrize(
        "range, query", [((3, 4), "3<=key<=4"), ((0, 0), "0<=key<=0")]
    )
    def test_compute_query_dict(self, range, query):
        bb = BaseBar(x="key")
        bb.chart_type = "bar"
        self.dashboard.add_charts([bb])
        bb.filter_widget.value = range
        # test the following function behavior
        bb.compute_query_dict(self.dashboard._query_str_dict)

        assert self.dashboard._query_str_dict["key_bar"] == query

    @pytest.mark.parametrize(
        "event, result", [(None, None), (ButtonClick, "func_Called")]
    )
    def test_add_events(self, event, result):
        bb = BaseBar(x="key")
        self.result = None

        def test_func(cls):
            self.result = "func_Called"

        bb.add_reset_event = test_func
        bb.reset_event = event
        # test the following function behavior
        bb.add_events(self.dashboard)

        assert self.result == result

    def test_add_reset_event(self):
        bb = BaseBar(x="key")
        self.result = None

        def test_func(event, callback):
            self.result = callback

        bb.add_event = test_func
        # test the following function behavior
        bb.add_reset_event(self.dashboard)
        assert self.result.__name__ == "reset_callback"
