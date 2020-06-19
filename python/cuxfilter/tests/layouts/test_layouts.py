import pytest

# module under test
import cuxfilter.layouts.layouts as m
from cuxfilter import charts, DataFrame, themes
import re
import cudf


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


class Test_layouts:
    charts_list = [
        charts.bar("key"),
        charts.drop_down("val"),
        charts.range_slider("val"),
    ]
    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = DataFrame.from_dataframe(df)

    dashboard = cux_df.dashboard(charts=charts_list, title="test_title")

    @pytest.mark.parametrize(
        "layout, len_charts",
        [
            (m.Layout0, 1),
            (m.Layout1, 2),
            (m.Layout2, 2),
            (m.Layout3, 3),
            (m.Layout4, 3),
            (m.Layout5, 3),
            (m.Layout6, 4),
            (m.Layout7, 4),
            (m.Layout8, 5),
            (m.Layout9, 6),
            (m.Layout10, 6),
            (m.Layout11, 6),
            (m.Layout12, 9),
        ],
    )
    def test_generate_dashboard(self, layout, len_charts):
        re_charts = re.compile("\\[chart")
        layout_ = layout()
        tmpl = layout_.generate_dashboard(
            "test", self.dashboard._charts, themes.dark
        )
        assert len(re_charts.findall(str(tmpl))) == len_charts
