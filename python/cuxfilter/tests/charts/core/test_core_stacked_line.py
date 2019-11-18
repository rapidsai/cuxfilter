import pytest
import cudf

from cuxfilter.charts.core.non_aggregate.core_stacked_line import (
    BaseStackedLine,
)
from cuxfilter.layouts import chart_view
import cuxfilter


class TestBaseStackedLine:
    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title="test_title")

    def test_variables(self):
        bsl = BaseStackedLine(x="key", y=["val"])

        # BaseChart variables
        assert bsl.chart_type == "stacked_lines"
        assert bsl.x == "key"
        assert bsl.y == ["val"]
        assert bsl.data_points == 100
        assert bsl.add_interaction is True
        assert bsl._stride is None
        assert bsl.stride_type == int
        assert bsl.height == 400
        assert bsl.width == 800
        assert bsl._library_specific_params == {}
        assert bsl.chart is None
        assert bsl.source is None
        assert bsl.source_backup is None
        assert bsl.min_value == 0.0
        assert bsl.max_value == 0.0
        assert bsl.name == "key_stacked_lines"

        # BaseStackedLineChart variables
        assert bsl.use_data_tiles is False
        assert bsl.reset_event is None
        assert bsl.x_range is None
        assert bsl.y_range is None
        assert bsl.colors == []

    def test_exceptions(self):
        with pytest.raises(TypeError):
            BaseStackedLine(x="key", y="val")
            BaseStackedLine(x="key", y=["val"], colors="color1")
        with pytest.raises(ValueError):
            BaseStackedLine(x="key", y=[])

    def test_initiate_chart(self):
        bsl = BaseStackedLine(x="key", y=["val"])
        bsl.initiate_chart(self.dashboard)

        assert bsl.x_range == (0, 4)
        assert bsl.y_range == (10, 14)

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bsl = BaseStackedLine(x="key", y=["val"])
        bsl.chart = chart
        bsl.width = 400

        assert str(bsl.view()) == str(chart_view(_chart, width=bsl.width))

    def test_calculate_source(self):
        bsl = BaseStackedLine(x="key", y=["val"])
        bsl.initiate_chart(self.dashboard)
        self.result = None

        def func1(data):
            self.result = data

        bsl.format_source_data = func1
        bsl.calculate_source(self.df)
        assert self.result.equals(self.df)

    def test_get_selection_geometry_callback(self):
        bsl = BaseStackedLine(x="key", y=["val"])

        assert (
            bsl.get_selection_geometry_callback(self.dashboard).__name__
            == "selection_callback"
        )
        assert callable(
            type(bsl.get_selection_geometry_callback(self.dashboard))
        )

    def test_selection_callback(self):
        bsl = BaseStackedLine("key", ["val"])
        self.dashboard._active_view = bsl.name
        t = bsl.get_selection_geometry_callback(self.dashboard)
        t(xmin=1, xmax=2, ymin=3, ymax=4)

        assert (
            self.dashboard._query_str_dict["key_stacked_lines"]
            == "1<=key <= 2"
        )

    @pytest.mark.parametrize(
        "x_range, y_range, query",
        [((1, 2), (3, 4), "1<=a <= 2"), ((0, 2), (3, 5), "0<=a <= 2")],
    )
    def test_compute_query_dict(self, x_range, y_range, query):
        bsl = BaseStackedLine("a", ["b"])
        bsl.x_range = x_range
        bsl.y_range = y_range
        df = cudf.DataFrame([("a", [1, 2, 2]), ("b", [3, 4, 5])])
        dashboard = cuxfilter.dashboard.DashBoard(data=df)
        bsl.compute_query_dict(dashboard._query_str_dict)

        assert dashboard._query_str_dict["a_stacked_lines"] == query

    @pytest.mark.parametrize(
        "add_interaction, reset_event, event_1, event_2",
        [
            (True, None, "selection_callback", None),
            (True, "test_event", "selection_callback", "reset_callback"),
            (False, "test_event", None, "reset_callback"),
        ],
    )
    def test_add_events(self, add_interaction, reset_event, event_1, event_2):
        bsl = BaseStackedLine("a", ["b"])
        bsl.add_interaction = add_interaction
        bsl.reset_event = reset_event
        df = cudf.DataFrame([("a", [1, 2, 2]), ("b", [3, 4, 5])])
        dashboard = cuxfilter.dashboard.DashBoard(data=df)
        self.event_1 = None
        self.event_2 = None

        def t_func(fn):
            self.event_1 = fn.__name__

        def t_func1(event, fn):
            self.event_2 = fn.__name__

        bsl.add_selection_geometry_event = t_func
        bsl.add_event = t_func1
        bsl.add_events(dashboard)

        assert self.event_1 == event_1
        assert self.event_2 == event_2

    def test_add_reset_event(self):
        bsl = BaseStackedLine("a", ["b"])
        bsl.x_range = (0, 2)
        bsl.y_range = (3, 5)

        df = cudf.DataFrame([("a", [1, 2, 2]), ("b", [3, 4, 5])])
        dashboard = cuxfilter.dashboard.DashBoard(data=df)
        dashboard._active_view = "a_stacked_lines"

        def t_func1(event, fn):
            fn("event")

        bsl.add_event = t_func1

        bsl.add_reset_event(dashboard)

        assert bsl.x_range is None
        assert bsl.y_range is None
        assert dashboard._active_view == "a_stacked_lines"

    def test_query_chart_by_range(self):
        bsl = BaseStackedLine("a", ["b"])
        bsl_1 = BaseStackedLine("b", ["a"])
        query_tuple = (4, 5)
        df = cudf.DataFrame([("a", [1, 2, 3, 4]), ("b", [3, 4, 5, 6])])
        bsl.source = df
        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bsl.reload_chart = t_func
        bsl.query_chart_by_range(
            active_chart=bsl_1, query_tuple=query_tuple, datatile=None
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
        bsl = BaseStackedLine("a", ["b"])
        bsl_1 = BaseStackedLine("b", ["a"])
        new_indices = new_indices
        df = cudf.DataFrame([("a", [1, 2, 3, 4]), ("b", [3, 4, 5, 6])])
        bsl.source = df
        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bsl.reload_chart = t_func
        bsl.query_chart_by_indices(
            active_chart=bsl_1,
            old_indices=[],
            new_indices=new_indices,
            datatile=None,
        )

        assert self.result.to_string() == result
        assert self.patch_update is False
