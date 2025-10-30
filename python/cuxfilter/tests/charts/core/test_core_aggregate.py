# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import pytest
import panel as pn

from cuxfilter.charts.core.aggregate.core_aggregate import BaseAggregateChart
from cuxfilter.charts.bokeh.plots.bar import InteractiveBar
import cuxfilter
from ..utils import initialize_df, df_types
from unittest import mock

df_args = {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
dfs = [initialize_df(type, df_args) for type in df_types]
cux_dfs = [cuxfilter.DataFrame.from_dataframe(df) for df in dfs]
# create cudf and dask_cudf backed cuxfilter dataframes
dashboards = [
    cux_df.dashboard(charts=[], title="test_title") for cux_df in cux_dfs
]


class TestBaseAggregateChart:
    def test_variables(self):
        bb = BaseAggregateChart(x="test_x")

        assert bb.chart_type is None
        assert bb.x == "test_x"
        assert bb.y is None
        assert bb.data_points is None
        assert bb.add_interaction is True
        assert bb.aggregate_fn == "count"
        assert bb.stride is None
        assert bb.stride_type is int
        assert bb.library_specific_params == {}

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_initiate_chart(self, dashboard):
        bb = BaseAggregateChart(x="key")
        bb.add_events = mock.Mock()
        bb.initiate_chart(dashboard)
        assert bb.min_value == 0.0
        assert bb.max_value == 4.0
        assert bb.stride is None
        assert bb.stride_type is int

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bac = BaseAggregateChart(x="test_x", add_interaction=False)
        bac.add_events = mock.Mock()
        bac.chart = chart

        assert str(bac.view()) == str(pn.panel(_chart, width=600, height=400))

    @pytest.mark.parametrize("dashboard", dashboards)
    @pytest.mark.parametrize(
        "range, query, local_dict",
        [
            (
                (3, 4),
                "@key_min<=key<=@key_max",
                {"key_min": 3, "key_max": 4},
            ),
            (
                (0, 0),
                "@key_min<=key<=@key_max",
                {"key_min": 0, "key_max": 0},
            ),
        ],
    )
    def test_compute_query_dict(self, dashboard, range, query, local_dict):
        bb = BaseAggregateChart(x="key")
        bb.add_events = mock.Mock()
        bb.chart_type = "bar"
        dashboard.add_charts([bb])
        bb.box_selected_range = {"key_min": range[0], "key_max": range[1]}
        # test the following function behavior
        bb.compute_query_dict(
            dashboard._query_str_dict,
            dashboard._query_local_variables_dict,
        )

        assert dashboard._query_str_dict[f"key_count_bar_{bb.title}"] == query
        for key in local_dict:
            assert (
                dashboard._query_local_variables_dict[key] == local_dict[key]
            )

    @pytest.mark.parametrize("dashboard", dashboards)
    @pytest.mark.parametrize(
        "event_1, event_2",
        [
            ("cb", "reset_callback"),
        ],
    )
    def test_add_events(
        self,
        dashboard,
        event_1,
        event_2,
    ):
        bnac = BaseAggregateChart(x="key")
        bnac.chart = InteractiveBar()

        self.event_1 = None
        self.event_2 = None

        def t_func(fn):
            self.event_1 = fn.__name__

        def t_func1(fn):
            self.event_2 = fn.__name__

        bnac.chart.add_box_select_callback = t_func
        bnac.chart.add_reset_callback = t_func1

        bnac.add_events(dashboard)

        assert self.event_1 == event_1
        assert self.event_2 == event_2
