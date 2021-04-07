import pytest

from cuxfilter.charts.core.core_widget import BaseWidget
from cuxfilter.layouts import chart_view


class TestBaseWidget:
    def test_variables(self):
        bw = BaseWidget("test_x", value=1, label_map={"temp": 1})

        assert bw.chart_type is None
        assert bw.x == "test_x"
        assert bw.color is None
        assert bw.height == 10
        assert bw.width == 400
        assert bw.chart is None
        assert bw.data_points is None
        assert bw.start is None
        assert bw.end is None
        assert bw._stride is None
        assert bw.stride_type == int
        assert bw.min_value == 0.0
        assert bw.max_value == 0.0
        assert bw.use_data_tiles is False
        assert bw.value == 1
        assert bw.label_map == {1: "temp"}
        assert bw.params == {}

        assert bw.compute_query_dict({}) is None
        assert bw.reload_chart() == -1

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bw = BaseWidget("test_x")
        bw.chart = chart

        assert str(bw.view()) == str(
            chart_view(_chart, width=bw.width, title="test_x_widget")
        )

    def test_add_event(self):
        bw = BaseWidget("test_x")

        from bokeh.events import ButtonClick
        from bokeh.models import Button

        def callback(event):
            # Python:Click
            pass

        bw.chart = Button()
        bw.add_event(ButtonClick, callback)

        assert ButtonClick.event_name in bw.chart.subscribed_events
