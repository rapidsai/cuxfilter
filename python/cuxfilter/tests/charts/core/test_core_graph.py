import pytest
import cudf

from cuxfilter.charts.core.non_aggregate.core_graph import BaseGraph
from cuxfilter.dashboard import DashBoard
from cuxfilter.charts.datashader.custom_extensions import CustomInspectTool
from cuxfilter import DataFrame
from cuxfilter.layouts import chart_view
from cuxfilter.charts import constants


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
        assert bg.width == 800
        assert bg.height == 400
        assert bg.title == ""
        assert bg.timeout == 100
        assert bg.chart_type is None
        assert bg.use_data_tiles is False
        assert bg.reset_event is None

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bg = BaseGraph()
        bg.chart = chart
        bg.width = 400

        assert str(bg.view()) == str(chart_view(_chart, width=bg.width))

    def test_get_selection_geometry_callback(self):
        bg = BaseGraph()

        df = cudf.DataFrame({"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        assert (
            bg.get_selection_geometry_callback(dashboard).__name__
            == "selection_callback"
        )
        assert callable(type(bg.get_selection_geometry_callback(dashboard)))

    @pytest.mark.parametrize(
        "inspect_neighbors, result", [
            (
                CustomInspectTool(_active=True),
                cudf.DataFrame({
                    'vertex': [0, 1, 2, 3],
                    'x': [0, 1, 1, 2],
                    'y': [0, 1, 2, 0]
                })
            ),
            (
                CustomInspectTool(_active=False),
                cudf.DataFrame({
                    'vertex': [1, 3],
                    'x': [1, 2],
                    'y': [1, 0]
                })
            )
        ]
    )
    def test_selection_callback(self, inspect_neighbors, result):
        nodes = cudf.DataFrame({
            'vertex': [0, 1, 2, 3],
            'x': [0, 1, 1, 2],
            'y': [0, 1, 2, 0]
        })
        edges = cudf.DataFrame({
            'source': [1, 1, 1, 1],
            'target': [0, 1, 2, 3]
        })
        dashboard = DashBoard(dataframe=DataFrame.load_graph((nodes, edges)))

        bg = BaseGraph()
        bg.chart_type = "temp"
        bg.nodes = nodes
        bg.edges = edges
        bg.inspect_neighbors = inspect_neighbors
        print(bg.inspect_neighbors._active)
        self.result = None

        def t_function(nodes, edges=None, patch_update=False):
            self.result = nodes.reset_index(drop=True)

        bg.reload_chart = t_function

        dashboard._active_view = bg.name

        t = bg.get_selection_geometry_callback(dashboard)
        t(xmin=1, xmax=3, ymin=0, ymax=1)
        assert self.result.equals(result)

    @pytest.mark.parametrize(
        "x_range, y_range, query",
        [
            ((1, 2), (3, 4), "1<=x <= 2 and 3<=y <= 4"),
            ((0, 2), (3, 5), "0<=x <= 2 and 3<=y <= 5"),
        ],
    )
    def test_compute_query_dict(self, x_range, y_range, query):
        bg = BaseGraph()
        bg.chart_type = "test"
        bg.x_range = x_range
        bg.y_range = y_range

        df = cudf.DataFrame({"x": [1, 2, 2], "y": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        bg.compute_query_dict(dashboard._query_str_dict)
        print(dashboard._query_str_dict)
        assert dashboard._query_str_dict["x_test"] == query

    @pytest.mark.parametrize(
        "add_interaction, reset_event, event_1, event_2",
        [
            (True, None, "selection_callback", None),
            (True, "test_event", "selection_callback", "reset_callback"),
            (False, "test_event", None, "reset_callback"),
        ],
    )
    def test_add_events(self, add_interaction, reset_event, event_1, event_2):
        bg = BaseGraph()
        bg.add_interaction = add_interaction
        bg.reset_event = reset_event

        df = cudf.DataFrame({"x": [1, 2, 2], "y": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        self.event_1 = None
        self.event_2 = None

        def t_func(fn):
            self.event_1 = fn.__name__

        def t_func1(event, fn):
            self.event_2 = fn.__name__

        bg.add_selection_geometry_event = t_func
        bg.add_event = t_func1

        bg.add_events(dashboard)

        assert self.event_1 == event_1
        assert self.event_2 == event_2

    def test_add_reset_event(self):
        bg = BaseGraph()
        bg.chart_type = "test"
        bg.x = "a"
        bg.x_range = (0, 2)
        bg.y_range = (3, 5)

        df = cudf.DataFrame({"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))
        dashboard._active_view = "a_test"

        def t_func1(event, fn):
            fn("event")

        bg.add_event = t_func1

        bg.add_reset_event(dashboard)

        assert bg.x_range is None
        assert bg.y_range is None
        assert dashboard._active_view == "a_test"

    def test_query_chart_by_range(self):
        bg = BaseGraph()
        bg.chart_type = "test"
        bg.x = "a"

        bg_1 = BaseGraph()
        bg_1.chart_type = "test"
        bg_1.x = "b"

        query_tuple = (4, 5)

        df = cudf.DataFrame({"a": [1, 2, 3, 4], "b": [3, 4, 5, 6]})
        bg.nodes = df

        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bg.reload_chart = t_func

        bg.query_chart_by_range(
            active_chart=bg_1, query_tuple=query_tuple, datatile=None
        )

        assert self.result.to_string() == "   a  b\n1  2  4\n2  3  5"
        assert self.patch_update is False

    @pytest.mark.parametrize(
        "new_indices, result",
        [
            ([4, 5], "   a  b\n1  2  4\n2  3  5"),
            ([], "   a  b\n0  1  3\n1  2  4\n2  3  5\n3  4  6"),
            ([3], "   a  b\n0  1  3"),
        ],
    )
    def test_query_chart_by_indices(self, new_indices, result):
        bg = BaseGraph()
        bg.chart_type = "test"
        bg.x = "a"

        bg_1 = BaseGraph()
        bg_1.chart_type = "test"
        bg_1.x = "b"

        new_indices = new_indices

        df = cudf.DataFrame({"a": [1, 2, 3, 4], "b": [3, 4, 5, 6]})
        bg.nodes = df

        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bg.reload_chart = t_func

        bg.query_chart_by_indices(
            active_chart=bg_1,
            old_indices=[],
            new_indices=new_indices,
            datatile=None,
        )

        assert self.result.to_string() == result
        assert self.patch_update is False
