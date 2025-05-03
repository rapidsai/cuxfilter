import dask_cudf
import pytest
import panel as pn
import cudf
import numpy as np

from cuxfilter.charts.core.non_aggregate.core_graph import BaseGraph
from cuxfilter.charts.datashader.custom_extensions import (
    holoviews_datashader as hv_dt,
)
import holoviews as hv
from cuxfilter.dashboard import DashBoard
from cuxfilter.charts.datashader.custom_extensions import CustomInspectTool
from cuxfilter import DataFrame
from cuxfilter.charts import constants
from unittest import mock

from ..utils import df_equals, df_types, initialize_df


def hv_test_cb():
    return pn.pane.HoloViews(hv.Curve([1, 2, 3]))


class TestCoreGraph:
    def test_variables(self):
        bg = BaseGraph()

        # BaseGraph variables
        assert bg.node_x == "x"
        assert bg.node_y == "y"
        assert bg.node_id == "vertex"
        assert bg.edge_source == "source"
        assert bg.edge_target == "target"
        assert bg.x_range is None
        assert bg.y_range is None
        assert bg.add_interaction is True
        assert bg.node_aggregate_col == "vertex"
        assert bg.edge_aggregate_col is None
        assert bg.node_aggregate_fn == "count"
        assert bg.edge_aggregate_fn == "count"
        assert bg.node_color_palette == constants.CUXF_DEFAULT_COLOR_PALETTE
        assert bg.edge_color_palette == ["#000000"]
        assert bg.node_point_size == 1
        assert bg.node_point_shape == "circle"
        assert bg.node_pixel_shade_type == "eq_hist"
        assert bg.node_pixel_density == 0.5
        assert bg.node_pixel_spread == "dynspread"
        assert bg.tile_provider == "CARTODBPOSITRON"
        assert bg.title == ""
        assert bg.timeout == 100
        assert bg.chart_type is None
        assert bg.use_data_tiles is False
        assert bg.reset_event is None

    def test_view(self):
        bg = BaseGraph()
        bg.chart = mock.Mock(
            **{"view.return_value": hv.DynamicMap(hv_test_cb)}
        )

        assert isinstance(bg.view(), pn.pane.HoloViews)

    @pytest.mark.parametrize("df_type", df_types)
    def test_get_selection_geometry_callback(self, df_type):
        bg = BaseGraph()

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        assert callable(type(bg.get_box_select_callback(dashboard)))
        assert callable(type(bg.get_lasso_select_callback(dashboard)))

    @pytest.mark.parametrize(
        "df_type, inspect_neighbors, result, index",
        [
            (
                cudf.DataFrame,
                CustomInspectTool(_active=True),
                {
                    "vertex": [0, 1, 2, 3],
                    "x": [0, 1, 1, 2],
                    "y": [0, 1, 2, 0],
                },
                [0, 1, 2, 3],
            ),
            (
                cudf.DataFrame,
                CustomInspectTool(_active=False),
                {"vertex": [1, 3], "x": [1, 2], "y": [1, 0]},
                [0, 1],
            ),
            (
                dask_cudf.DataFrame,
                CustomInspectTool(_active=True),
                {
                    "vertex": [0, 1, 2, 3],
                    "x": [0, 1, 1, 2],
                    "y": [0, 1, 2, 0],
                },
                [0, 1, 2, 3],
            ),
            (
                dask_cudf.DataFrame,
                CustomInspectTool(_active=False),
                {"vertex": [1, 3], "x": [1, 2], "y": [1, 0]},
                [0, 0],
            ),
        ],
    )
    def test_box_selection_callback(
        self, df_type, inspect_neighbors, result, index
    ):
        nodes = initialize_df(
            df_type,
            {"vertex": [0, 1, 2, 3], "x": [0, 1, 1, 2], "y": [0, 1, 2, 0]},
        )
        edges = initialize_df(
            df_type, {"source": [1, 1, 1, 1], "target": [0, 1, 2, 3]}
        )
        dashboard = DashBoard(dataframe=DataFrame.load_graph((nodes, edges)))

        bg = BaseGraph()
        bg.chart_type = "temp"
        bg.nodes = nodes
        bg.edges = edges
        bg.inspect_neighbors = inspect_neighbors
        self.result = None

        def t_function(data, edges=None, patch_update=False):
            self.result = data.sort_values(by="vertex").reset_index(drop=True)

        bg.reload_chart = t_function

        dashboard._active_view = bg

        class evt:
            bounds = (1, 3, 0, 1)
            x_selection = (1, 3)
            y_selection = (0, 1)

        t = bg.get_box_select_callback(dashboard)
        t(evt.bounds, evt.x_selection, evt.y_selection)

        result = initialize_df(df_type, result, index)
        assert df_equals(self.result, result)

    @pytest.mark.parametrize("df_type", df_types)
    def test_lasso_selection_callback(self, df_type):
        nodes = initialize_df(
            df_type,
            {"vertex": [0, 1, 2, 3], "x": [0, 1, 1, 2], "y": [0, 1, 2, 0]},
        )
        edges = initialize_df(
            df_type, {"source": [1, 1, 1, 1], "target": [0, 1, 2, 3]}
        )
        dashboard = DashBoard(dataframe=DataFrame.load_graph((nodes, edges)))

        bg = BaseGraph()
        bg.chart_type = "graph_lasso_test"
        bg.nodes = nodes  # Make sure BaseGraph instance knows the nodes
        bg.edges = edges
        bg.inspect_neighbors = CustomInspectTool(_active=False)

        self.result = None  # Reset result for the test

        def t_function(data, edges=None, patch_update=False):
            # Store the result sorted by vertex for consistent comparison
            # Handle empty DataFrame case
            if data is not None and len(data) > 0:
                self.result = data.sort_values(by="vertex").reset_index(
                    drop=True
                )
            elif data is not None:  # Empty dataframe
                self.result = data
            else:  # data is None
                self.result = None

        bg.reload_chart = t_function
        # Define the lasso polygon - square from (1,1) to (2,2)
        geometry = np.array(
            [[1.0, 1.0], [1.0, 2.0], [2.0, 2.0], [2.0, 1.0], [1.0, 1.0]],
            dtype=np.float64,
        )

        # Get the callback function
        lasso_callback = bg.get_lasso_select_callback(dashboard)
        # Execute the callback with the geometry
        lasso_callback(geometry=geometry)

        # --- Expected Result Definition ---
        # Only node 1 (vertex=1, x=1, y=1) should be selected
        expected_nodes_data = {
            "vertex": [1],
            "x": [1],
            "y": [1],
        }
        # Always create the expected result as a cudf.DataFrame
        expected_cudf_df = cudf.DataFrame(expected_nodes_data)

        # --- Comparison Logic ---
        assert self.result is not None

        # Compute the result if it's a Dask DataFrame
        if isinstance(self.result, dask_cudf.DataFrame):
            result_to_compare = self.result.compute()
        else:
            result_to_compare = self.result

        # Ensure result is sorted and indexed like the expected one
        if result_to_compare is not None and len(result_to_compare) > 0:
            result_to_compare = result_to_compare.sort_values(
                by="vertex"
            ).reset_index(drop=True)

        # Assert the content matches the expected selected nodes
        # df_equals likely uses cudf.testing.assert_frame_equal internally
        assert df_equals(result_to_compare, expected_cudf_df)

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
        bg = BaseGraph()
        bg.chart_type = "test"
        bg.box_selected_range = local_dict
        bg.x_range = x_range
        bg.y_range = y_range

        df = initialize_df(df_type, {"x": [1, 2, 2], "y": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        bg.compute_query_dict(
            dashboard._query_str_dict, dashboard._query_local_variables_dict
        )
        assert (
            dashboard._query_str_dict[f"x_y_vertex_count_test_{bg.title}"]
            == query
        )
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
        bg = BaseGraph()
        bg.add_interaction = add_interaction
        bg.reset_event = reset_event
        bg.chart = hv_dt.InteractiveDatashader()

        df = initialize_df(df_type, {"x": [1, 2, 2], "y": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        self.event_1 = None
        self.event_2 = None

        def t_func(fn):
            self.event_1 = fn.__name__

        def t_func1(fn):
            self.event_2 = fn.__name__

        bg.chart.add_box_select_callback = t_func
        bg.chart.add_lasso_select_callback = t_func1

        bg.add_events(dashboard)

        assert self.event_1 == event_1
        assert self.event_2 == event_2

    @pytest.mark.parametrize("df_type", df_types)
    def test_add_reset_event(self, df_type):
        bg = BaseGraph()
        bg.edges = None
        bg.chart_type = "test"
        bg.x = "a"
        bg.x_range = (0, 2)
        bg.y_range = (3, 5)
        bg.chart = hv_dt.InteractiveDatashader()

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))
        dashboard._active_view = bg

        def t_func1(event, fn):
            fn("event")

        def reload_fn(data, edges=None, patch_update=False):
            pass

        bg.add_event = t_func1
        bg.reload_chart = reload_fn
        bg.add_reset_event(dashboard)

        assert bg.selected_indices is None
