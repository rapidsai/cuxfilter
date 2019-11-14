import pytest
import cudf
from bokeh.events import ButtonClick

from cuXfilter.charts.core.aggregate.core_aggregate_choropleth import (
    BaseChoropleth,
)
import cuXfilter
from cuXfilter.layouts import chart_view
from cuXfilter.assets import geo_json_mapper


class TestBaseCholorpleth:

    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuXfilter.DataFrame.from_dataframe(df)
    geoJSONSource = "./test.geojson"

    def test_variables(self):
        bc = BaseChoropleth(
            x="key", geoJSONSource=self.geoJSONSource, nan_color="white"
        )
        result = geo_json_mapper(self.geoJSONSource, None)

        assert bc.chart_type == "choropleth"
        assert bc.reset_event is None
        assert bc._datatile_loaded_state is False
        assert bc.geo_mapper == result[0]
        assert bc.use_data_tiles is True
        assert bc.x == "key"
        assert bc.y is None
        assert bc.data_points == int(100)
        assert bc.add_interaction is True
        assert bc.aggregate_fn == "count"
        assert bc.width == 800
        assert bc.height == 400
        assert bc.stride is None
        assert bc.stride_type == int
        assert bc.geoJSONSource == self.geoJSONSource
        assert bc.geoJSONProperty is None
        assert bc.geo_color_palette is None
        assert bc.tile_provider is None
        assert bc.library_specific_params["x_range"] == result[1]
        assert bc.library_specific_params["y_range"] == result[2]
        assert "nan_color" not in bc.library_specific_params
        assert bc.nan_color == "white"

    def test_initiate_chart(self):
        bc = BaseChoropleth(
            x="key", geoJSONSource=self.geoJSONSource, nan_color="white"
        )
        dashboard = self.cux_df.dashboard(charts=[bc], title="test_title")

        bc.initiate_chart(dashboard)

        assert bc.min_value == 0.0
        assert bc.max_value == 4.0
        assert bc.data_points == 5
        assert bc.stride == 1
        assert bc.stride_type == int

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bc = BaseChoropleth(
            x="key", geoJSONSource=self.geoJSONSource, nan_color="white"
        )
        bc.chart = chart
        bc.width = 400

        assert str(bc.view()) == str(chart_view(_chart, width=bc.width))

    @pytest.mark.parametrize(
        "bc, aggregate_fn, result",
        [
            (
                BaseChoropleth(
                    x="key",
                    y="val",
                    geoJSONSource="./test.geojson",
                    nan_color="white",
                ),
                "mean",
                {
                    "X": [0.0, 1.0, 2.0, 3.0, 4.0],
                    "Y": [10.0, 11.0, 12.0, 13.0, 14.0],
                },
            ),
            (
                BaseChoropleth(
                    x="key", geoJSONSource="./test.geojson", nan_color="white"
                ),
                "count",
                {
                    "X": [0.0, 0.8, 1.6, 2.4000000000000004, 4.0],
                    "Y": [1, 1, 1, 1, 1],
                },
            ),
        ],
    )
    def test_calculate_source(self, bc, aggregate_fn, result):
        self.result = None
        dashboard = self.cux_df.dashboard(charts=[bc], title="test_title")
        bc.initiate_chart(dashboard)

        def func1(dict_temp, patch_update=False):
            self.result = dict_temp

        bc.aggregate_fn = aggregate_fn
        bc.format_source_data = func1
        bc.calculate_source(self.df)

        assert self.result == result

    @pytest.mark.parametrize(
        "old, new", [([1], [1, 2]), ([], [1]), ([1], [2])]
    )
    def test_get_selection_callback(self, old, new):
        bc = BaseChoropleth(
            x="key",
            y="val",
            geoJSONSource=self.geoJSONSource,
            nan_color="white",
        )
        dashboard = self.cux_df.dashboard(charts=[bc], title="test_title")
        self.result = None

        def func1(old, new):
            self.result = (old, new)

        dashboard._query_datatiles_by_indices = func1
        fn_test = bc.get_selection_callback(dashboard)
        fn_test(old, new)

        assert fn_test.__name__ == "selection_callback"
        assert self.result == (old, new)

    def test_compute_query_dict(self):
        bc = BaseChoropleth(
            x="key",
            y="val",
            geoJSONSource=self.geoJSONSource,
            nan_color="white",
        )
        dashboard = self.cux_df.dashboard(charts=[bc], title="test_title")
        bc.min_value = dashboard._data[bc.x].min()
        bc.max_value = dashboard._data[bc.x].max()

        def test_func():
            return [0, 1, 2]

        bc.get_selected_indices = test_func
        if bc.data_points > dashboard._data[bc.x].shape[0]:
            bc.data_points = dashboard._data[bc.x].shape[0]
        # test the following function behavior
        bc.compute_query_dict(dashboard._query_str_dict)
        dashboard._query_str_dict

        assert dashboard._query_str_dict["key_choropleth"] == "key in (0,1,2)"

    @pytest.mark.parametrize(
        "event, add_interaction, result1, result2",
        [
            (None, True, None, "selection_callback"),
            (ButtonClick, False, "func_Called", None),
        ],
    )
    def test_add_events(self, event, add_interaction, result1, result2):
        bc = BaseChoropleth(
            x="key",
            y="val",
            geoJSONSource=self.geoJSONSource,
            nan_color="white",
        )
        dashboard = self.cux_df.dashboard(charts=[bc], title="test_title")
        bc.add_interaction = add_interaction
        self.result1 = None
        self.result2 = None

        def func1(cls):
            self.result1 = "func_Called"

        def func2(callback):
            self.result2 = callback.__name__

        bc.add_reset_event = func1
        bc.add_selection_event = func2
        bc.reset_event = event
        # test the following function behavior
        bc.add_events(dashboard)

        assert self.result1 == result1
        assert self.result2 == result2

    def test_add_reset_event(self):
        bc = BaseChoropleth(
            x="key",
            y="val",
            geoJSONSource=self.geoJSONSource,
            nan_color="white",
        )
        dashboard = self.cux_df.dashboard(charts=[bc], title="test_title")
        self.result = None

        def test_func(event, callback):
            self.result = callback

        bc.add_event = test_func
        # test the following function behavior
        bc.add_reset_event(dashboard)
        assert self.result.__name__ == "reset_callback"

    def test_get_selected_indices(self):
        bc = BaseChoropleth(
            x="key",
            y="val",
            geoJSONSource=self.geoJSONSource,
            nan_color="white",
        )
        assert bc.get_selected_indices() == []
