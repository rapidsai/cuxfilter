# SPDX-FileCopyrightText: Copyright (c) 2020-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
import panel as pn
from bokeh.events import ButtonClick

import cuxfilter
from cuxfilter.charts.core.non_aggregate.core_line import BaseLine
from cuxfilter.charts.datashader.custom_extensions import (
    holoviews_datashader as hv_dt,
)
import holoviews as hv
from unittest import mock

from ..utils import initialize_df, df_types

df_args = {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
dfs = [initialize_df(type, df_args) for type in df_types]
cux_dfs = [cuxfilter.DataFrame.from_dataframe(df) for df in dfs]
# create cudf and dask_cudf backed cuxfilter dataframes
dashboards = [
    cux_df.dashboard(charts=[], title="test_title") for cux_df in cux_dfs
]


def hv_test_cb():
    return pn.pane.HoloViews(hv.Curve([1, 2, 3]))


class TestNonAggregateBaseLine:
    def test_variables(self):
        bl = BaseLine(x="test_x", y="test_y", color="#8735fb")
        assert bl.x == "test_x"
        assert bl.y == "test_y"
        assert bl.filter_widget is None
        assert bl.stride is None
        assert bl.stride_type is int
        assert bl.pixel_shade_type == "linear"
        assert bl.color == "#8735fb"
        assert bl.library_specific_params == {}
        assert bl.data_points == 100
        assert bl.add_interaction is True
        assert bl.chart_type is None

    def test_view(self):
        bl = BaseLine(x="test_x", y="test_y")
        bl.chart = mock.Mock(
            **{"view.return_value": hv.DynamicMap(hv_test_cb)}
        )

        assert isinstance(bl.view(), pn.pane.HoloViews)

    @pytest.mark.parametrize("dashboard", dashboards)
    @pytest.mark.parametrize(
        "x_range, y_range, query, local_dict",
        [
            (
                (1, 2),
                (3, 4),
                "@x_min<=x<=@x_max and @y_min<=y<=@y_max",
                {"x_min": 1, "x_max": 2, "y_min": 3, "y_max": 4},
            ),
            (
                (0, 2),
                (3, 5),
                "@x_min<=x<=@x_max and @y_min<=y<=@y_max",
                {"x_min": 0, "x_max": 2, "y_min": 3, "y_max": 5},
            ),
        ],
    )
    def test_compute_query_dict(
        self, dashboard, x_range, y_range, query, local_dict
    ):
        bl = BaseLine(x="x", y="y", title="custom_title")
        bl.chart_type = "non_aggregate_line"
        bl.box_selected_range = local_dict
        bl.chart = hv_dt.InteractiveDatashader()
        bl.x_range = x_range
        bl.y_range = y_range

        dashboard.add_charts([bl])
        # test the following function behavior
        bl.compute_query_dict(
            dashboard._query_str_dict,
            dashboard._query_local_variables_dict,
        )

        assert (
            dashboard._query_str_dict["x_y_non_aggregate_line_custom_title"]
            == query
        )
        for key in local_dict:
            assert (
                dashboard._query_local_variables_dict[key] == local_dict[key]
            )

    @pytest.mark.parametrize("dashboard", dashboards)
    @pytest.mark.parametrize(
        "event, result", [(None, None), (ButtonClick, "func_Called")]
    )
    def test_add_events(self, dashboard, event, result):
        bl = BaseLine(x="key", y="val")
        bl.chart = hv_dt.InteractiveDatashader()
        self.result = None

        def test_func(cls):
            self.result = "func_Called"

        bl.add_reset_event = test_func
        bl.reset_event = event
        # test the following function behavior
        bl.add_events(dashboard)

        assert self.result == result

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_add_reset_event(self, dashboard):
        bl = BaseLine(x="key", y="val")
        bl.chart = hv_dt.InteractiveDatashader()
        self.result = None

        def test_func(event, callback):
            self.result = callback

        bl.add_event = test_func
        # test the following function behavior
        bl.add_reset_event(dashboard)
        assert bl.selected_indices is None
