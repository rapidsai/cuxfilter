import pytest

# module under test
import cuxfilter.layouts.layouts as m


class _Chart:
    def __init__(self, chart_type):
        self.chart_type = chart_type


class Test_is_widget:
    @pytest.mark.parametrize(
        "chart_type", ["widget", "foo widget", "foo widget bar"]
    )
    def test_identifies_widget_in_chart_type(self, chart_type):
        c = _Chart(chart_type)
        assert m.is_widget(c)

    def test_identifies_datasize_indicator(self):
        c = _Chart("datasize_indicator")
        assert m.is_widget(c)

    def test_identifies_non_widget_otherwise(self):
        c = _Chart("plot")
        assert not m.is_widget(c)
