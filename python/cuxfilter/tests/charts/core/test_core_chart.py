import pytest

from cuxfilter.charts.core.core_chart import BaseChart


class TestBaseChart:
    def test_variables(self):
        bc = BaseChart()
        assert bc.chart_type is None
        assert bc.x is None
        assert bc.y is None
        assert bc.aggregate_fn == "count"
        assert bc.color is None
        assert bc.height == 0
        assert bc.width == 0
        assert bc.add_interaction is True
        assert bc.chart is None
        assert bc.source is None
        assert bc.source_backup is None
        assert bc.data_points == 0
        assert bc._library_specific_params == {}
        assert bc.stride is None
        assert bc.stride_type == int
        assert bc.min_value == 0.0
        assert bc.max_value == 0.0
        assert bc.x_label_map == {}
        assert bc.y_label_map == {}
        assert bc.title == ""

        bc.x = "test_x"
        bc.chart_type = "test_chart_type"

        assert bc.name == "test_x_test_chart_type_"

    def test_set_dimensions(self):
        bc = BaseChart()
        bc.chart = 1
        bc.filter_widget = (
            BaseChart()
        )  # setting filter_widget to some chart object
        bc.width = 400
        bc.height = 400
        assert bc.width == 400
        assert bc.filter_widget.width == 400
        assert bc.height == 400

    def test_label_mappers(self):
        bc = BaseChart()
        library_specific_params = {
            "x_label_map": {"a": 1, "b": 2},
            "y_label_map": {"a": 1, "b": 2},
        }
        bc.library_specific_params = library_specific_params
        bc.extract_mappers()

        assert bc.x_label_map == {"a": 1, "b": 2}
        assert bc.y_label_map == {"a": 1, "b": 2}

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        bc = BaseChart()
        bc.chart = chart
        assert bc.view() == _chart

    def test_set_color(self):
        bc = BaseChart()
        library_specific_params = {"color": "blue"}
        bc.library_specific_params = library_specific_params
        bc.set_color()

        assert bc.color == "blue"

    def test_umimplemented_fns(self):
        bc = BaseChart()
        assert bc.update_dimensions() == -1
        assert bc.calculate_source(data={}) == -1
        assert bc.generate_chart() == -1
        assert bc.add_reset_event() == -1
        assert bc.compute_query_dict(query_dict={}) == -1
        assert bc.reset_chart() == -1
        assert bc.reload_chart(data={}, patch_update=False) == -1
        assert bc.reload_chart(data={}, patch_update=True) == -1
        assert bc.format_source_data(source_dict={}, patch_update=False) == -1
        assert bc.format_source_data(source_dict={}, patch_update=True) == -1
        assert bc.apply_mappers() == -1
        assert bc.get_source_y_axis() == []
