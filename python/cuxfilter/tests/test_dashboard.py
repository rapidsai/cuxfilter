import pytest

import cuxfilter
from cuxfilter.charts import bokeh, panel_widgets
import cudf


class TestDashBoard:
    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title="test_title")
    _datasize_title = "_datasize_indicator_Datapoints Selected"

    def test_variables(self):
        assert self.dashboard._cuxfilter_df.data.equals(self.df)
        assert self.dashboard.title == "test_title"
        assert (
            self.dashboard._dashboard.__class__
            == cuxfilter.layouts.single_feature
        )
        assert self.dashboard._theme == cuxfilter.themes.default

        assert list(self.dashboard._sidebar.keys()) == [self._datasize_title]
        assert self.dashboard._query_str_dict == {}

    def test_add_charts(self):
        dashboard = self.cux_df.dashboard(charts=[], title="test_title")
        bac = bokeh.bar("key")
        for _ in range(3):
            bac = bokeh.bar("key")
            bac.chart_type = "chart_" + str(_ + 1)
            dashboard.add_charts(charts=[bac])

        assert list(dashboard._charts.keys()) == [
            f"key_count_chart_1_{bac.title}",
            f"key_count_chart_2_{bac.title}",
            f"key_count_chart_3_{bac.title}",
        ]

    def test_add_sidebar(self):
        dashboard = self.cux_df.dashboard(charts=[], title="test_title")
        dashboard1 = self.cux_df.dashboard(charts=[], title="test_title")
        bac = bokeh.bar("key")
        for _ in range(3):
            bac = bokeh.bar("key")
            bac.chart_type = "chart_" + str(_ + 1)
            dashboard.add_charts(sidebar=[bac])

        for i in range(3):
            dashboard1.add_charts(
                sidebar=[panel_widgets.card(content=f"test{i}")]
            )

        assert len(dashboard._charts) == 0
        assert len(dashboard._sidebar) == 1
        assert list(dashboard._sidebar.keys()) == [self._datasize_title]
        assert len(dashboard1._charts) == 0
        assert len(dashboard1._sidebar) == 4
        for i in range(3):
            assert "card" in list(dashboard1._sidebar.keys())[i + 1]

    @pytest.mark.parametrize(
        "query, result",
        [
            (
                "key<3",
                "   key   val\n0    0  10.0\n1    1  11.0\n2    2  12.0",
            ),
            (
                "key>=3",
                "   key   val\n3    3  13.0\n4    4  14.0",
            ),
        ],
    )
    def test_query(self, query, result):
        df = cudf.DataFrame(
            {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
        )
        cux_df = cuxfilter.DataFrame.from_dataframe(df.copy())
        dashboard = cux_df.dashboard(charts=[], title="test_title")
        query_res = dashboard._query(query_str=query)

        assert query_res.to_string() == result

    @pytest.mark.parametrize(
        "query_dict, query_str",
        [({"col_1_chart": "6<=col_1<=9"}, "6<=col_1<=9"), ({}, "")],
    )
    def test__generate_query_str(self, query_dict, query_str):
        self.dashboard._query_str_dict = query_dict
        assert self.dashboard._generate_query_str() == query_str

    def test_export(self):
        dashboard = self.cux_df.dashboard(charts=[], title="test_title")
        bac = bokeh.bar("key")
        bac.chart_type = "chart_1"
        dashboard.add_charts([bac])
        bac.filter_widget.value = (0, 3)

        assert dashboard.export().equals(self.df[self.df.key.between(0, 3)])
