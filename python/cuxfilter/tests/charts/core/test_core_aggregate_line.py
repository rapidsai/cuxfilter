import pytest
import cudf
from bokeh.events import ButtonClick
import panel as pn

from cuxfilter.charts.core.aggregate.core_aggregate_line import BaseLine
import cuxfilter
from cuxfilter.layouts import chart_view


class TestBaseLine:

    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title="test_title")

    def test_variables(self):
        bl = BaseLine(x="test_x")

        assert bl.chart_type == "line"
        assert bl.reset_event is None
        assert bl._datatile_loaded_state is False
        assert bl.filter_widget is None
        assert bl.use_data_tiles is True
        assert bl.x == "test_x"
        assert bl.y is None
        assert bl.data_points == int(100)
        assert bl.add_interaction is True
        assert bl.aggregate_fn == "count"
        assert bl.width == 400
        assert bl.height == 400
        assert bl.stride is None
        assert bl.stride_type == int
        assert bl.library_specific_params == {}

    def test_initiate_chart(self):
        bl = BaseLine(x="key")
        bl.initiate_chart(self.dashboard)

        assert bl.min_value == 0.0
        assert bl.max_value == 4.0
        assert bl.data_points == 5
        assert bl.stride == 1
        assert bl.stride_type == int

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bl = BaseLine(x="test_x")
        bl.chart = chart
        bl.width = 400

        assert str(bl.view()) == str(chart_view(_chart, width=bl.width))

    @pytest.mark.parametrize(
        "bl, result",
        [
            (
                BaseLine(x="key", y="val"),
                {
                    "X": [0.0, 1.0, 2.0, 3.0, 4.0],
                    "Y": [10.0, 11.0, 12.0, 13.0, 14.0],
                },
            ),
            (
                BaseLine(x="key"),
                {
                    "X": [0.0, 1.0, 2.0, 3.0, 4.0],
                    "Y": [1.0, 1.0, 1.0, 1.0, 1.0],
                },
            ),
        ],
    )
    def test_calculate_source(self, bl, result):
        bl.initiate_chart(self.dashboard)
        self.result = None

        def func1(dict_temp, patch_update=False):
            self.result = dict_temp

        bl.format_source_data = func1
        bl.calculate_source(self.df)
        assert self.result == result

    def test_add_range_slider_filter(self):
        bl = BaseLine(x="key")
        bl.min_value = self.dashboard._data[bl.x].min()
        bl.max_value = self.dashboard._data[bl.x].max()
        if bl.data_points > self.dashboard._data[bl.x].shape[0]:
            bl.data_points = self.dashboard._data[bl.x].shape[0]
        bl.add_range_slider_filter(self.dashboard)

        assert type(bl.filter_widget) == pn.widgets.RangeSlider
        assert bl.filter_widget.value == (0, 4)

    @pytest.mark.parametrize(
        "range, query", [((3, 4), "3<=key<=4"), ((0, 0), "0<=key<=0")]
    )
    def test_compute_query_dict(self, range, query):
        bl = BaseLine(x="key")
        bl.min_value = self.dashboard._data[bl.x].min()
        bl.max_value = self.dashboard._data[bl.x].max()
        bl.stride = 1
        if bl.data_points > self.dashboard._data[bl.x].shape[0]:
            bl.data_points = self.dashboard._data[bl.x].shape[0]
        bl.add_range_slider_filter(self.dashboard)
        self.dashboard.add_charts([bl])
        bl.filter_widget.value = range
        # test the following function behavior
        bl.compute_query_dict(self.dashboard._query_str_dict)

        assert self.dashboard._query_str_dict["key_line"] == query

    @pytest.mark.parametrize(
        "event, result", [(None, None), (ButtonClick, "func_Called")]
    )
    def test_add_events(self, event, result):
        bl = BaseLine(x="key")
        self.result = None

        def test_func(cls):
            self.result = "func_Called"

        bl.add_reset_event = test_func
        bl.reset_event = event
        # test the following function behavior
        bl.add_events(self.dashboard)

        assert self.result == result

    def test_add_reset_event(self):
        bl = BaseLine(x="key")
        self.result = None

        def test_func(event, callback):
            self.result = callback

        bl.add_event = test_func
        # test the following function behavior
        bl.add_reset_event(self.dashboard)
        assert self.result.__name__ == "reset_callback"
