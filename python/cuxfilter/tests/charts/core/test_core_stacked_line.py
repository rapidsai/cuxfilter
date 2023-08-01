import pytest
import panel as pn
import dask.dataframe as dd
import dask_cudf
import cuxfilter

from cuxfilter.charts.core.non_aggregate.core_stacked_line import (
    BaseStackedLine,
)
from cuxfilter.charts.datashader.custom_extensions import (
    holoviews_datashader as hv,
)
from unittest import mock

from ..utils import df_equals, initialize_df, df_types

df_args = {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
dfs = [initialize_df(type, df_args) for type in df_types]
cux_dfs = [cuxfilter.DataFrame.from_dataframe(df) for df in dfs]
# create cudf and dask_cudf backed cuxfilter dataframes
dashboards = [
    cux_df.dashboard(charts=[], title="test_title") for cux_df in cux_dfs
]


class TestBaseStackedLine:
    def test_variables(self):
        bsl = BaseStackedLine(x="key", y=["val"])

        # BaseChart variables
        assert bsl.x == "key"
        assert bsl.y == ["val"]
        assert bsl.data_points == 100
        assert bsl.add_interaction is True
        assert bsl.stride is None
        assert bsl.stride_type == int
        assert bsl.height == 400
        assert bsl.width == 800
        assert bsl._library_specific_params == {}
        assert bsl.chart is None
        assert bsl.source is None
        assert bsl.source_backup is None
        assert bsl.min_value == 0.0
        assert bsl.max_value == 0.0
        assert bsl.chart_type is None
        # BaseStackedLineChart variables
        assert bsl.use_data_tiles is False
        assert bsl.reset_event is None
        assert bsl.x_range is None
        assert bsl.y_range is None
        assert bsl.colors == ["#8735fb"]

    def test_exceptions(self):
        with pytest.raises(TypeError):
            BaseStackedLine(x="key", y="val")
            BaseStackedLine(x="key", y=["val"], colors="color1")
        with pytest.raises(ValueError):
            BaseStackedLine(x="key", y=[])

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_initiate_chart(self, dashboard):
        bsl = BaseStackedLine(x="key", y=["val"])
        bsl.chart = hv.InteractiveDatashader()
        bsl.initiate_chart(dashboard)

        if isinstance(dashboard._cuxfilter_df.data, dask_cudf.DataFrame):
            # incase base dataframe is a dask.dataframe
            bsl.x_range = dd.compute(*bsl.x_range)
            bsl.y_range = dd.compute(*bsl.y_range)

        assert bsl.x_range == (0, 4)
        assert bsl.y_range == (10, 14)

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bsl = BaseStackedLine(x="key", y=["val"])
        bsl.chart = mock.Mock(**{"view.return_value": chart})
        bsl.width = 400

        assert str(bsl.view()) == str(pn.panel(_chart, width=bsl.width))

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_calculate_source(self, dashboard):
        bsl = BaseStackedLine(x="key", y=["val"])
        bsl.chart = hv.InteractiveDatashader()
        bsl.initiate_chart(dashboard)
        self.result = None

        def func1(data):
            self.result = data

        bsl.format_source_data = func1
        bsl.calculate_source(dashboard._cuxfilter_df.data)
        assert df_equals(self.result, dashboard._cuxfilter_df.data)

    @pytest.mark.parametrize("dashboard", dashboards)
    def test_get_selection_geometry_callback(self, dashboard):
        bsl = BaseStackedLine(x="key", y=["val"])
        assert callable(type(bsl.get_box_select_callback(dashboard)))

    @pytest.mark.parametrize("df_type", df_types)
    def test_box_selection_callback(self, df_type):
        bsl = BaseStackedLine("a", ["b"])
        bsl.chart_type = "stacked_lines"

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = cuxfilter.dashboard.DashBoard(
            dataframe=cuxfilter.DataFrame.from_dataframe(df)
        )
        dashboard._active_view = bsl

        t = bsl.get_box_select_callback(dashboard)
        t(boundsx=(1, 2))

        result_query = dashboard._generate_query_str()
        query_variables = dashboard._query_local_variables_dict
        assert result_query == "@a_min<=a<=@a_max"
        assert query_variables["a_min"] == 1
        assert query_variables["a_max"] == 2

        result_df = dashboard._query(dashboard._generate_query_str())
        expected_df = df.query("1<=a<=2")
        assert df_equals(result_df, expected_df)

    @pytest.mark.parametrize("df_type", df_types)
    @pytest.mark.parametrize(
        "x_range, y_range, query, local_dict",
        [
            (
                (1, 2),
                (3, 4),
                "@x_min<=x<=@x_max",
                {"x_min": 1, "x_max": 2},
            ),
            (
                (0, 2),
                (3, 5),
                "@x_min<=x<=@x_max",
                {"x_min": 0, "x_max": 2},
            ),
        ],
    )
    def test_compute_query_dict(
        self, df_type, x_range, y_range, query, local_dict
    ):
        bsl = BaseStackedLine("x", ["y"])
        bsl.chart_type = "stacked_lines"
        bsl.x_range = x_range
        bsl.y_range = y_range
        bsl.box_selected_range = local_dict
        df = initialize_df(df_type, {"x": [1, 2, 2], "y": [3, 4, 5]})
        dashboard = cuxfilter.dashboard.DashBoard(
            dataframe=cuxfilter.DataFrame.from_dataframe(df)
        )
        bsl.compute_query_dict(
            dashboard._query_str_dict, dashboard._query_local_variables_dict
        )
        assert (
            dashboard._query_str_dict[
                f"x_{'_'.join(['y'])}_stacked_lines_{bsl.title}"
            ]
            == query
        )
        for key in local_dict:
            assert (
                dashboard._query_local_variables_dict[key] == local_dict[key]
            )

    @pytest.mark.parametrize("df_type", df_types)
    @pytest.mark.parametrize(
        "add_interaction, reset_event, event_1",
        [
            (True, None, "cb"),
            (True, "test_event", "cb"),
            (False, "test_event", None),
        ],
    )
    def test_add_events(self, df_type, add_interaction, reset_event, event_1):
        bsl = BaseStackedLine("a", ["b"])
        bsl.chart = hv.InteractiveDatashader()
        bsl.add_interaction = add_interaction
        bsl.reset_event = reset_event
        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = cuxfilter.dashboard.DashBoard(
            dataframe=cuxfilter.DataFrame.from_dataframe(df)
        )
        self.event_1 = None
        self.event_2 = None

        def t_func(fn):
            self.event_1 = fn.__name__

        bsl.chart.add_box_select_callback = t_func
        bsl.add_events(dashboard)

        assert self.event_1 == event_1

    @pytest.mark.parametrize("df_type", df_types)
    def test_add_reset_event(self, df_type):
        bsl = BaseStackedLine("a", ["b"])
        bsl.chart_type = "stacked_lines"
        bsl.chart = hv.InteractiveDatashader()
        bsl.x_range = (0, 2)
        bsl.y_range = (3, 5)

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = cuxfilter.dashboard.DashBoard(
            dataframe=cuxfilter.DataFrame.from_dataframe(df)
        )
        dashboard._active_view = bsl

        def t_func1(event, fn):
            fn("event")

        bsl.add_event = t_func1

        bsl.add_reset_event(dashboard)

        assert (
            f"x_{'_'.join(['y'])}_stacked_lines_{bsl.title}"
            not in dashboard._query_str_dict
        )
