import pytest

import cuxfilter
from cuxfilter.charts import bokeh
import cudf
import pandas as pd
import numpy as np


class TestDashBoard:

    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title="test_title")

    def test_variables(self):
        assert self.dashboard._cuxfilter_df.data.equals(self.df)
        assert self.dashboard.title == "test_title"
        assert (
            self.dashboard._dashboard.__class__
            == cuxfilter.layouts.single_feature
        )
        assert self.dashboard._theme == cuxfilter.themes.light
        assert self.dashboard.data_size_widget is True
        assert list(self.dashboard._charts.keys()) == ["_datasize_indicator"]
        assert self.dashboard._data_tiles == {}
        assert self.dashboard._query_str_dict == {}
        assert self.dashboard._active_view == ""

    def test_add_charts(self):
        bac = bokeh.bar("key")
        bac.chart_type = "chart_1"
        for _ in range(3):
            bac = bokeh.bar("key")
            bac.chart_type = "chart_" + str(_ + 1)
            self.dashboard.add_charts([bac])

        assert list(self.dashboard._charts.keys()) == [
            "_datasize_indicator",
            "key_chart_1",
            "key_chart_2",
            "key_chart_3",
        ]

    @pytest.mark.parametrize(
        "query, result",
        [
            (
                "key<3",
                "   key   val\n0    0  10.0\n1    1  11.0\n2    2  12.0",
            ),
            ("key>=3", "   key   val\n3    3  13.0\n4    4  14.0",),
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

    @pytest.mark.parametrize(
        "active_view, result",
        [
            (
                "",
                (
                    "   key   val\n0    0  10.0\n1    1  11.0\n2"
                    "    2  12.0\n3    3  13.0\n4    4  14.0"
                ),
            ),
            (
                "key_chart_1",
                (
                    "   key   val\n0    0  10.0\n1    1  11.0\n2"
                    "    2  12.0\n3    3  13.0"
                ),
            ),
        ],
    )
    def test_export(self, active_view, result):
        dashboard = self.cux_df.dashboard(charts=[], title="test_title")

        bac = bokeh.bar("key")
        bac.chart_type = "chart_1"
        dashboard.add_charts([bac])
        bac.filter_widget.value = (0, 3)
        dashboard._active_view = active_view

        assert dashboard.export().to_string() == result

    # unit tests for datatile and query functions are already
    # present in core_aggregate and core_non_aggregate test files

    # integrated tests
    @pytest.mark.parametrize(
        "active_view, passive_view, result",
        [
            (
                "key_line",
                "val_bar",
                pd.DataFrame(
                    {
                        0: {0: 1.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                        1: {0: 1.0, 1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0},
                        2: {0: 1.0, 1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0},
                        3: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 0.0},
                        4: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
                    }
                ),
            ),
            ("val_bar", "key_line", None),
        ],
    )
    def test_calc_data_tiles(self, active_view, passive_view, result):
        df = cudf.DataFrame(
            {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
        )
        cux_df = cuxfilter.DataFrame.from_dataframe(df)
        bac = bokeh.line("key", "val")
        bac.use_data_tiles = False
        bac1 = bokeh.bar("val")
        dashboard = cux_df.dashboard(
            charts=[bac, bac1],
            title="test_title",
            layout=cuxfilter.layouts.double_feature,
        )
        dashboard._active_view = active_view
        dashboard._calc_data_tiles()

        if result is None:
            assert dashboard._data_tiles[passive_view] is result
        else:
            assert dashboard._data_tiles[passive_view].equals(result)

        assert (
            dashboard._charts[dashboard._active_view].datatile_loaded_state
            is True
        )

    @pytest.mark.parametrize(
        "query_tuple, result",
        [
            ((2, 4), [0, 0, 1, 1, 1]),
            ((2, 2), [0, 0, 1, 0, 0]),
            ((0, 0), [1, 0, 0, 0, 0]),
            ((0, 4), [1, 1, 1, 1, 1]),
        ],
    )
    def test_query_datatiles_by_range(self, query_tuple, result):
        df = cudf.DataFrame(
            {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
        )
        cux_df = cuxfilter.DataFrame.from_dataframe(df)
        bac = bokeh.line("key", "val")
        bac1 = bokeh.bar("val")
        dashboard = cux_df.dashboard(
            charts=[bac, bac1],
            title="test_title",
            layout=cuxfilter.layouts.double_feature,
        )
        dashboard._active_view = bac.name
        dashboard._calc_data_tiles()
        dashboard._query_datatiles_by_range(query_tuple=query_tuple)

        assert all(bac1.source.data["top"] == result)

    @pytest.mark.parametrize(
        "old_indices, new_indices, prev_result, result",
        [
            ([], [1], [1, 1, 1, 1, 1], [0, 1, 0, 0, 0]),
            ([1], [1], [0, 1, 0, 0, 0], [0, 1, 0, 0, 0]),
            ([1], [1, 2], [0, 1, 0, 0, 0], [0, 1, 1, 0, 0]),
            ([1, 2], [2], [0, 1, 1, 0, 0], [0, 0, 1, 0, 0]),
        ],
    )
    def test_query_datatiles_by_indices(
        self, old_indices, new_indices, prev_result, result
    ):
        df = cudf.DataFrame(
            {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
        )
        cux_df = cuxfilter.DataFrame.from_dataframe(df)
        bac = bokeh.line("key", "val")
        bac1 = bokeh.bar("val")
        dashboard = cux_df.dashboard(
            charts=[bac, bac1],
            title="test_title",
            layout=cuxfilter.layouts.double_feature,
        )
        dashboard._active_view = bac.name
        dashboard._calc_data_tiles(cumsum=False)

        bac1.source.data["top"] = np.array(prev_result)
        dashboard._charts["_datasize_indicator"].reset_chart(len(old_indices))
        dashboard._query_datatiles_by_indices(
            old_indices=old_indices, new_indices=new_indices
        )

        assert all(bac1.source.data["top"] == result)

    def test_reset_current_view(self):
        df = cudf.DataFrame(
            {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
        )
        cux_df = cuxfilter.DataFrame.from_dataframe(df)
        bac = bokeh.line("key", "val")
        bac1 = bokeh.bar("val")
        dashboard = cux_df.dashboard(
            charts=[bac, bac1],
            title="test_title",
            layout=cuxfilter.layouts.double_feature,
        )
        dashboard._active_view = bac.name
        dashboard._calc_data_tiles()
        dashboard._query_datatiles_by_range(query_tuple=(1, 2))
        bac.filter_widget.value = (1, 2)

        # reset active view
        dashboard._reset_current_view(new_active_view=bac1)

        assert dashboard._active_view == bac1.name
        assert dashboard._query_str_dict == {
            "key_line": "@key_min <= key <= @key_max"
        }
        assert dashboard._query_local_variables_dict == {
            "key_min": 1,
            "key_max": 2,
        }
        assert dashboard._charts[bac.name].datatile_loaded_state is False
        assert bac1.name not in dashboard._query_str_dict
