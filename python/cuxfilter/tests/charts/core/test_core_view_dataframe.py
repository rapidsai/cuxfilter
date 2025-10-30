# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
import panel as pn
import cuxfilter

from cuxfilter.charts.core.core_view_dataframe import ViewDataFrame
import holoviews as hv

from ..utils import df_equals, initialize_df, df_types

df_args = {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
df_duplicate_args = {"key": [0, 1, 1, 1, 4], "val": [10, 11, 11, 11, 14]}

dfs = [initialize_df(type, df_args) for type in df_types]
df_duplicates = [initialize_df(type, df_duplicate_args) for type in df_types]

cux_dfs = [cuxfilter.DataFrame.from_dataframe(df) for df in dfs]

# create cudf and dask_cudf backed cuxfilter dataframes
dashboards = [
    cux_df.dashboard(charts=[], title="test_title") for cux_df in cux_dfs
]


class TestViewDataFrame:
    def test_variables(self):
        vd = ViewDataFrame()

        vd.columns is None
        vd.use_data_tiles is False
        vd.source is None
        vd.chart is None
        vd.drop_duplicates is False

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_initiate_chart(self, dashboard):
        vd = ViewDataFrame()
        assert vd.columns is None

        vd.initiate_chart(dashboard)

        assert str(vd.chart) == str(hv.Table(dashboard._cuxfilter_df.data))
        assert vd.columns == list(dashboard._cuxfilter_df.data.columns)

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        vd = ViewDataFrame()
        vd.chart = chart

        assert str(vd.view()) == str(pn.panel(_chart, width=600, height=400))

    @pytest.mark.parametrize(
        "dashboard, df_duplicate",
        [(dashboards[0], df_duplicates[0]), (dashboards[1], df_duplicates[1])],
    )
    @pytest.mark.parametrize("drop_duplicates", [True, False])
    def test_reload_chart(self, dashboard, df_duplicate, drop_duplicates):
        vd = ViewDataFrame(drop_duplicates=drop_duplicates)
        vd.initiate_chart(dashboard)

        vd.reload_chart(df_duplicate)

        if drop_duplicates:
            assert df_equals(vd.chart.data, df_duplicate.drop_duplicates())
        else:
            assert df_equals(vd.chart.data, df_duplicate)
