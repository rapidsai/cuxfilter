import pytest ; pytest

import pandas as pd
import numpy as np
from cuXfilter.charts.core.aggregate.core_aggregate import BaseAggregateChart

class TestCoreAggregateChart():
    
    def test_variables(self):
        bac = BaseAggregateChart()

        #BaseChart variables
        assert bac.chart_type == None
        assert bac.x == None
        assert bac.y == None
        assert bac.aggregate_fn == 'count'
        assert bac.color == None
        assert bac.height == 0
        assert bac.width == 0
        assert bac.add_interaction == True
        assert bac.chart == None
        assert bac.source == None
        assert bac.source_backup == None
        assert bac.data_points == 0
        assert bac._library_specific_params == {}
        assert bac._stride == None
        assert bac.stride_type == int
        assert bac.min_value == 0.0
        assert bac.max_value == 0.0
        assert bac.x_label_map == {}
        assert bac.y_label_map == {}

        bac.x = 'test_x'
        bac.chart_type = 'test_chart_type'

        assert bac.name == 'test_x_test_chart_type'


        #BaseAggregateChart variables
        assert bac.use_data_tiles == True

    @pytest.mark.parametrize("stride, _stride", [(1,1),(None, None), (0,1)])
    def test_stride(self, stride, _stride):
        bac = BaseAggregateChart()
        bac.stride = stride
        assert bac._stride == _stride

    
    def test_label_mappers(self):
        bac = BaseAggregateChart()
        library_specific_params = {
            'x_label_map': {'a':1, 'b':2},
            'y_label_map':{'a':1, 'b':2}
        }
        bac.library_specific_params = library_specific_params

        assert bac.x_label_map == {'a':1, 'b':2}
        assert bac.y_label_map == {'a':1, 'b':2}

    @pytest.mark.parametrize('chart, _chart',[(None, None),(1,1)])
    def test_view(self, chart, _chart):
        bac = BaseAggregateChart()
        bac.chart = chart
        assert bac.view() == _chart

    def test_query_chart_by_range(self):
        active_chart = BaseAggregateChart()
        
        active_chart.stride = 8
        active_chart.min_value = 10.0

        self.result = ''
        
        def reset_chart(datatile_result):
            self.result = datatile_result

        active_chart.reset_chart = reset_chart

        query_tuple = (10,26)

        datatile = pd.DataFrame({0: {0: 0.0, 1: 0.0, 2: 0.0, 4: 0.0, 5: 4.0},
                        1: {0: 0.0, 1: 0.0, 2: 0.0, 4: 3.0, 5: 4.0},
                        2: {0: 0.0, 1: 0.0, 2: 2.0, 4: 3.0, 5: 4.0},
                        3: {0: 0.0, 1: 1.0, 2: 2.0, 4: 3.0, 5: 4.0},
                        4: {0: 0.0, 1: 1.0, 2: 2.0, 4: 3.0, 5: 4.0},
                        5: {0: 0.0, 1: 1.0, 2: 2.0, 4: 3.0, 5: 4.0}})

        active_chart.query_chart_by_range(active_chart, query_tuple, datatile)

        assert all([0.0, 0.0, 0.0,  3.0,  4.0] == self.result)