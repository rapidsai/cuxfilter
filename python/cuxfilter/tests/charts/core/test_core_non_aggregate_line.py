import pytest
import cudf
import panel as pn
from bokeh.events import ButtonClick


import cuxfilter
from cuxfilter.charts.core.non_aggregate.core_line import BaseLine
from cuxfilter.layouts import chart_view


class TestNonAggregateBaseLine:

    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title="test_title")

    def test_variables(self):
        bl = BaseLine(x="test_x", y="test_y", color="#8735fb")
        assert bl.x == "test_x"
        assert bl.y == "test_y"
        assert bl.filter_widget is None
        assert bl.stride is None
        assert bl.stride_type == int
        assert bl.width == 800
        assert bl.height == 400
        assert bl.pixel_shade_type == "linear"
        assert bl.color == "#8735fb"
        assert bl.library_specific_params == {}
        assert bl.data_points == 100
        assert bl.add_interaction is True
        assert bl.chart_type is None

    def test_initiate_chart(self):
        bl = BaseLine(x="key", y="val")
        bl.initiate_chart(self.dashboard)

        assert bl.min_value == 0.0
        assert bl.max_value == 4.0
        assert bl.data_points == 5
        assert bl.stride == 1
        assert bl.stride_type == int

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bl = BaseLine(x="test_x", y="test_y")
        bl.chart = chart
        bl.width = 400

        assert str(bl.view()) == str(chart_view(_chart, width=bl.width))

    def test_add_range_slider_filter(self):
        bl = BaseLine(x="key", y="val")
        bl.min_value = self.dashboard._cuxfilter_df.data[bl.x].min()
        bl.max_value = self.dashboard._cuxfilter_df.data[bl.x].max()
        if bl.data_points > self.dashboard._cuxfilter_df.data[bl.x].shape[0]:
            bl.data_points = self.dashboard._cuxfilter_df.data[bl.x].shape[0]
        bl.compute_stride()
        bl.add_range_slider_filter(self.dashboard)

        assert isinstance(bl.filter_widget, pn.widgets.RangeSlider)
        assert bl.filter_widget.value == (0, 4)

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
    def test_compute_query_dict(self, range, query, local_dict):
        bb = BaseLine(x="key", y="val")
        bb.chart_type = "non_aggregate_line"
        self.dashboard.add_charts([bb])
        bb.filter_widget.value = range
        # test the following function behavior
        bb.compute_query_dict(
            self.dashboard._query_str_dict,
            self.dashboard._query_local_variables_dict,
        )

        assert (
            self.dashboard._query_str_dict["key_val_non_aggregate_line"]
            == query
        )
        for key in local_dict:
            assert (
                self.dashboard._query_local_variables_dict[key]
                == local_dict[key]
            )

    @pytest.mark.parametrize(
        "event, result", [(None, None), (ButtonClick, "func_Called")]
    )
    def test_add_events(self, event, result):
        bl = BaseLine(x="key", y="val")
        self.result = None

        def test_func(cls):
            self.result = "func_Called"

        bl.add_reset_event = test_func
        bl.reset_event = event
        # test the following function behavior
        bl.add_events(self.dashboard)

        assert self.result == result

    def test_add_reset_event(self):
        bl = BaseLine(x="key", y="val")
        self.result = None

        def test_func(event, callback):
            self.result = callback

        bl.add_event = test_func
        # test the following function behavior
        bl.add_reset_event(self.dashboard)
        assert self.result.__name__ == "reset_callback"
