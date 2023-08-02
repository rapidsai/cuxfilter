import panel as pn
from cuxfilter.charts.core.core_chart import BaseChart


class TestBaseChart:
    def test_variables(self):
        bc = BaseChart()
        assert bc.chart_type is None
        assert bc.x is None
        assert bc.y is None
        assert bc.aggregate_fn == "count"
        assert bc.color is None
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
        assert bc.x_label_map is None
        assert bc.y_label_map is None
        assert bc.title == ""

        bc.x = "test_x"
        bc.chart_type = "test_chart_type"

        assert bc.name == "test_x_test_chart_type_"

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

    def test_view(self):
        bc = BaseChart()
        panel = bc.view(width=800, height=600)
        assert isinstance(panel, pn.pane.PaneBase)
        assert panel.width == 800
        assert panel.height == 600

    def test_set_color(self):
        bc = BaseChart()
        library_specific_params = {"color": "blue"}
        bc.library_specific_params = library_specific_params
        bc.set_color()

        assert bc.color == "blue"

    def test_umimplemented_fns(self):
        bc = BaseChart()
        assert bc.calculate_source(data={}) == -1
        assert bc.generate_chart() == -1
        assert bc.add_reset_event() == -1
        assert bc.compute_query_dict(query_dict={}) == -1
        assert bc.reset_chart() == -1
        assert bc.reload_chart(data={}, patch_update=False) == -1
        assert bc.reload_chart(data={}) == -1
        assert bc.format_source_data(source_dict={}, patch_update=False) == -1
        assert bc.format_source_data(source_dict={}) == -1
        assert bc.apply_mappers() == -1
