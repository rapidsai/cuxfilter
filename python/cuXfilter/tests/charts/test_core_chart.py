import pytest ; pytest

from cuXfilter.charts.core.core_chart import BaseChart

class TestBaseChart():
    
    def test_variables(self):
        bc = BaseChart()
        assert bc.chart_type == None
        assert bc.x == None
        assert bc.y == None
        assert bc.aggregate_fn == 'count'
        assert bc.color == None
        assert bc.height == 0
        assert bc.width == 0
        assert bc.add_interaction == True
        assert bc.chart == None
        assert bc.source == None
        assert bc.source_backup == None
        assert bc.data_points == 0
        assert bc._library_specific_params == {}
        assert bc._stride == None
        assert bc.stride_type == int
        assert bc.min_value == 0.0
        assert bc.max_value == 0.0
        assert bc.x_label_map == {}
        assert bc.y_label_map == {}

        bc.x = 'test_x'
        bc.chart_type = 'test_chart_type'

        assert bc.name == 'test_x_test_chart_type'

    @pytest.mark.parametrize("stride, _stride", [(1,1),(None, None), (0,1)])
    def test_stride(self, stride, _stride):
        bc = BaseChart()
        bc.stride = stride
        assert bc._stride == _stride

    
    def test_label_mappers(self):
        bc = BaseChart()
        library_specific_params = {
            'x_label_map': {'a':1, 'b':2},
            'y_label_map':{'a':1, 'b':2}
        }
        bc.library_specific_params = library_specific_params

        assert bc.x_label_map == {'a':1, 'b':2}
        assert bc.y_label_map == {'a':1, 'b':2}

    @pytest.mark.parametrize('chart, _chart',[(None, None),(1,1)])
    def test_view(self, chart, _chart):
        bc = BaseChart()
        bc.chart = chart
        assert bc.view() == _chart