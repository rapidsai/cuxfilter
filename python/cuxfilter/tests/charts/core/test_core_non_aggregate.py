import pytest
import panel as pn
import cudf
import dask_cudf
import numpy as np

from cuxfilter.charts.datashader.custom_extensions import (
    holoviews_datashader as hv_dt,
)
import holoviews as hv
from cuxfilter.charts.core.non_aggregate.core_non_aggregate import (
    BaseNonAggregate,
)
from cuxfilter.dashboard import DashBoard
from cuxfilter import DataFrame
from unittest import mock

from ..utils import df_equals, df_types, initialize_df


def hv_test_cb():
    return pn.pane.HoloViews(hv.Curve([1, 2, 3]))


class TestCoreNonAggregateChart:
    def test_variables(self):
        bnac = BaseNonAggregate()

        # BaseChart variables
        assert bnac.chart_type is None
        assert bnac.x is None
        assert bnac.y is None
        assert bnac.aggregate_fn == "count"
        assert bnac.color is None
        assert bnac.add_interaction is True
        assert bnac.chart is None
        assert bnac.source is None
        assert bnac.source_backup is None
        assert bnac.data_points == 0
        assert bnac._library_specific_params == {}
        assert bnac.stride is None
        assert bnac.stride_type == int
        assert bnac.min_value == 0.0
        assert bnac.max_value == 0.0
        assert bnac.x_label_map is None
        assert bnac.y_label_map is None
        assert bnac.title == ""

        # test chart name setter
        bnac.x = "x"
        bnac.y = "y"
        bnac.chart_type = "test_chart_type"
        assert bnac.name == "x_y_count_test_chart_type_"

        # BaseNonAggregateChart variables
        assert bnac.use_data_tiles is False
        assert bnac.reset_event is None
        assert bnac.x_range is None
        assert bnac.y_range is None
        assert bnac.aggregate_col is None

    def test_label_mappers(self):
        bnac = BaseNonAggregate()
        library_specific_params = {
            "x_label_map": {"a": 1, "b": 2},
            "y_label_map": {"a": 1, "b": 2},
        }
        bnac.library_specific_params = library_specific_params

        assert bnac.x_label_map == {"a": 1, "b": 2}
        assert bnac.y_label_map == {"a": 1, "b": 2}

    def test_view(self):
        bnac = BaseNonAggregate()
        bnac.chart = mock.Mock(
            **{"view.return_value": hv.DynamicMap(hv_test_cb)}
        )

        assert isinstance(bnac.view(), pn.pane.HoloViews)

    @pytest.mark.parametrize("df_type", df_types)
    def test_get_selection_geometry_callback(self, df_type):
        bnac = BaseNonAggregate()

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        assert callable(type(bnac.get_box_select_callback(dashboard)))
        assert callable(type(bnac.get_lasso_select_callback(dashboard)))

    @pytest.mark.parametrize("df_type", df_types)
    def test_box_selection_callback(self, df_type):
        bnac = BaseNonAggregate()
        bnac.x = "a"
        bnac.y = "b"
        bnac.chart_type = "temp"

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        class evt:
            bounds = (1, 2, 3, 4)
            x_selection = (1, 2)
            y_selection = (3, 4)

        t = bnac.get_box_select_callback(dashboard)
        t(evt.bounds, evt.x_selection, evt.y_selection)

        result_query = dashboard._generate_query_str()
        query_variables = dashboard._query_local_variables_dict
        assert result_query == "@a_min<=a<=@a_max and @b_min<=b<=@b_max"
        assert query_variables["a_min"] == 1
        assert query_variables["a_max"] == 2
        assert query_variables["b_min"] == 3
        assert query_variables["b_max"] == 4

        result_df = dashboard._query(dashboard._generate_query_str())
        expected_df = df.query("1<=a<=2 and 3<=b<=4")
        assert df_equals(result_df, expected_df)

    @pytest.mark.parametrize("df_type", df_types)
    def test_lasso_selection_callback(self, df_type):
        bnac = BaseNonAggregate()
        bnac.x = "a"
        bnac.y = "b"
        bnac.chart_type = "non_agg_lasso_test"

        df = initialize_df(df_type, {"a": [0, 1, 1, 2], "b": [0, 1, 2, 0]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        # Define the lasso polygon - square from (1,1) to (2,2)
        geometry = np.array(
            [[1.0, 1.0], [1.0, 2.0], [2.0, 2.0], [2.0, 1.0], [1.0, 1.0]],
            dtype=np.float64,
        )

        # Get the callback function
        lasso_callback = bnac.get_lasso_select_callback(dashboard)

        # Execute the callback
        lasso_callback(geometry=geometry)

        # --- Expected Result Definition ---
        # Only point (a=1, b=1) should be selected
        expected_nodes_data = {
            "a": [1],
            "b": [1],
        }
        # Always create the expected result as a cudf.DataFrame
        expected_cudf_df = cudf.DataFrame(expected_nodes_data)
        # Ensure dtypes match the original for robust comparison
        expected_cudf_df["a"] = expected_cudf_df["a"].astype(df["a"].dtype)
        expected_cudf_df["b"] = expected_cudf_df["b"].astype(df["b"].dtype)

        # --- Comparison Logic ---
        # The callback updates the dashboard's query dictionary
        # We need to execute the query to get the selected data
        result_df = dashboard._query(dashboard._generate_query_str())

        assert result_df is not None

        # Compute the result if it's a Dask DataFrame
        if isinstance(result_df, dask_cudf.DataFrame):
            result_to_compare = result_df.compute()
        else:
            result_to_compare = result_df

        # Ensure result is sorted and indexed like the expected one
        if result_to_compare is not None and len(result_to_compare) > 0:
            result_to_compare = result_to_compare.sort_values(
                by=["a", "b"]
            ).reset_index(drop=True)

        expected_cudf_df = expected_cudf_df.sort_values(
            by=["a", "b"]
        ).reset_index(drop=True)

        # Assert the content matches the expected selected nodes
        assert isinstance(result_to_compare, cudf.DataFrame)
        assert df_equals(result_to_compare, expected_cudf_df)

    @pytest.mark.parametrize(
        "data, _data",
        [
            (cudf.DataFrame(), cudf.DataFrame()),
            (
                cudf.DataFrame({"a": [1, 2, 2], "b": [3, 4, 5]}),
                cudf.DataFrame({"a": [1, 2, 2], "b": [3, 4, 5]}),
            ),
            (
                initialize_df(dask_cudf.DataFrame, {}),
                initialize_df(dask_cudf.DataFrame, {}),
            ),
            (
                initialize_df(
                    dask_cudf.DataFrame, {"a": [1, 2, 2], "b": [3, 4, 5]}
                ),
                initialize_df(
                    dask_cudf.DataFrame, {"a": [1, 2, 2], "b": [3, 4, 5]}
                ),
            ),
        ],
    )
    def test_calculate_source(self, data, _data):
        """
        Calculate source just calls to the format_source_data function
        which is implemented by chart types inheriting this class.
        """
        bnac = BaseNonAggregate()
        self.result = None

        def t_function(data, patch_update=False):
            self.result = data

        bnac.format_source_data = t_function

        bnac.calculate_source(data)
        assert df_equals(self.result, _data)

    @pytest.mark.parametrize("df_type", df_types)
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
        self, df_type, x_range, y_range, query, local_dict
    ):
        bnac = BaseNonAggregate()
        bnac.chart_type = "test"
        bnac.x = "x"
        bnac.y = "y"
        bnac.box_selected_range = local_dict
        bnac.x_range = x_range
        bnac.y_range = y_range

        df = initialize_df(df_type, {"x": [1, 2, 2], "y": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        bnac.compute_query_dict(
            dashboard._query_str_dict, dashboard._query_local_variables_dict
        )

        bnac_key = (
            f"{bnac.x}_{bnac.y}"
            f"{'_' + bnac.aggregate_col if bnac.aggregate_col else ''}"
            f"_{bnac.aggregate_fn}_{bnac.chart_type}_{bnac.title}"
        )

        assert dashboard._query_str_dict[bnac_key] == query
        for key in local_dict:
            assert (
                dashboard._query_local_variables_dict[key] == local_dict[key]
            )

    @pytest.mark.parametrize("df_type", df_types)
    @pytest.mark.parametrize(
        "add_interaction, reset_event, event_1, event_2",
        [
            (True, None, "cb", "cb"),
            (True, "test_event", "cb", "cb"),
            (False, "test_event", None, None),
        ],
    )
    def test_add_events(
        self, df_type, add_interaction, reset_event, event_1, event_2
    ):
        bnac = BaseNonAggregate()
        bnac.add_interaction = add_interaction
        bnac.reset_event = reset_event
        bnac.chart = hv_dt.InteractiveDatashader()

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        self.event_1 = None
        self.event_2 = None

        def t_func(fn):
            self.event_1 = fn.__name__

        def t_func1(fn):
            self.event_2 = fn.__name__

        bnac.chart.add_box_select_callback = t_func
        bnac.chart.add_lasso_select_callback = t_func1

        bnac.add_events(dashboard)

        assert self.event_1 == event_1
        assert self.event_2 == event_2

    @pytest.mark.parametrize("df_type", df_types)
    def test_add_reset_event(self, df_type):
        bnac = BaseNonAggregate()
        bnac.chart_type = "test"
        bnac.x = "a"
        bnac.x_range = (0, 2)
        bnac.y_range = (3, 5)
        bnac.chart = hv_dt.InteractiveDatashader()

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))
        dashboard._active_view = bnac

        def t_func1(event, fn):
            fn("event")

        bnac.add_event = t_func1
        bnac.add_reset_event(dashboard)

        assert bnac.selected_indices is None
