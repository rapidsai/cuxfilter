import pytest
import cudf
import dask_cudf
import mock
import numpy as np

from cuxfilter.charts.datashader.custom_extensions import (
    holoviews_datashader as hv,
)
from cuxfilter.charts.core.non_aggregate.core_non_aggregate import (
    BaseNonAggregate,
)
from cuxfilter.dashboard import DashBoard
from cuxfilter import DataFrame
from cuxfilter.layouts import chart_view

from ..utils import df_equals, df_types, initialize_df


class TestCoreNonAggregateChart:
    def test_variables(self):
        bnac = BaseNonAggregate()

        # BaseChart variables
        assert bnac.chart_type is None
        assert bnac.x is None
        assert bnac.y is None
        assert bnac.aggregate_fn == "count"
        assert bnac.color is None
        assert bnac.height == 0
        assert bnac.width == 0
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
        assert bnac.x_label_map == {}
        assert bnac.y_label_map == {}
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

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bnac = BaseNonAggregate()
        bnac.chart = mock.Mock(**{"view.return_value": chart})
        bnac.width = 400
        bnac.title = "test_title"

        assert str(bnac.view()) == str(
            chart_view(_chart, width=bnac.width, title=bnac.title)
        )

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
        self.result = None

        def t_function(data, patch_update=False):
            self.result = data

        bnac.reload_chart = t_function
        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        dashboard._active_view = bnac

        class evt:
            bounds = (1, 2, 3, 4)
            x_selection = (1, 2)
            y_selection = (3, 4)

        t = bnac.get_box_select_callback(dashboard)
        t(evt.bounds, evt.x_selection, evt.y_selection)
        assert df_equals(self.result, df.query("1<=a<=2 and 3<=b<=4"))

    @pytest.mark.parametrize("df_type", df_types)
    def test_lasso_selection_callback(self, df_type):
        bnac = BaseNonAggregate()
        bnac.x = "a"
        bnac.y = "b"
        bnac.chart_type = "temp"

        def t_function(data, patch_update=False):
            self.result = data

        bnac.reload_chart = t_function
        df = initialize_df(df_type, {"a": [0, 1, 1, 2], "b": [0, 1, 2, 0]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))

        geometry = np.array([[1, 1, 2], [1, 2, 1]])

        t = bnac.get_lasso_select_callback(dashboard)
        with mock.patch("cuspatial.point_in_polygon") as pip:
            if isinstance(df, dask_cudf.DataFrame):
                # point in polygon is called per partition,
                # in this case 2 partitions of length 2 each
                pip.return_value = cudf.DataFrame({"selection": [True, False]})
            else:
                pip.return_value = cudf.DataFrame(
                    {"selection": [True, False, True, False]}
                )
            t(geometry)
            assert pip.called
            assert isinstance(self.result, df_type)

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
        bnac.chart = hv.InteractiveDatashader()

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
        bnac.chart = hv.InteractiveDatashader()

        df = initialize_df(df_type, {"a": [1, 2, 2], "b": [3, 4, 5]})
        dashboard = DashBoard(dataframe=DataFrame.from_dataframe(df))
        dashboard._active_view = bnac

        def t_func1(event, fn):
            fn("event")

        bnac.add_event = t_func1
        bnac.add_reset_event(dashboard)

        assert bnac.selected_indices is None

    @pytest.mark.parametrize("df_type", df_types)
    def test_query_chart_by_range(self, df_type):
        bnac = BaseNonAggregate()
        bnac.chart_type = "test"
        bnac.x = "a"

        bnac_1 = BaseNonAggregate()
        bnac_1.chart_type = "test"
        bnac_1.x = "b"

        query_tuple = (4, 5)

        df = initialize_df(df_type, {"a": [1, 2, 3, 4], "b": [3, 4, 5, 6]})
        bnac.source = df

        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bnac.reload_chart = t_func

        bnac.query_chart_by_range(
            active_chart=bnac_1, query_tuple=query_tuple, datatile=None
        )
        assert df_equals(
            self.result,
            initialize_df(df_type, {"a": [2, 3], "b": [4, 5]}, [1, 2]),
        )
        assert self.patch_update is False

    @pytest.mark.parametrize("df_type", df_types)
    @pytest.mark.parametrize(
        "new_indices, result, index",
        [
            ([4, 5], {"a": [2, 3], "b": [4, 5]}, [1, 2]),
            ([], {"a": [1, 2, 3, 4], "b": [3, 4, 5, 6]}, [0, 1, 2, 3]),
            ([3], {"a": [1], "b": [3]}, [0]),
        ],
    )
    def test_query_chart_by_indices(self, df_type, new_indices, result, index):
        bnac = BaseNonAggregate()
        bnac.chart_type = "test"
        bnac.x = "a"

        bnac_1 = BaseNonAggregate()
        bnac_1.chart_type = "test"
        bnac_1.x = "b"

        new_indices = new_indices

        df = initialize_df(df_type, {"a": [1, 2, 3, 4], "b": [3, 4, 5, 6]})
        bnac.source = df

        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bnac.reload_chart = t_func

        bnac.query_chart_by_indices(
            active_chart=bnac_1,
            old_indices=[],
            new_indices=new_indices,
            datatile=None,
        )
        result = initialize_df(df_type, result, index)

        assert df_equals(self.result, result)
        assert self.patch_update is False
