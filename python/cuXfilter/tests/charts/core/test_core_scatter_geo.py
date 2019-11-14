import pytest

from cuXfilter.charts.core.non_aggregate.core_scatter_geo import BaseScatterGeo

class TestBaseScatterGeo():

    def test_variables(self):
        bsg = BaseScatterGeo(x='test_x', y='test_y', aggregate_col='test_agg_col')

        assert bsg.chart_type == 'scatter-geo'
        assert bsg.x == 'test_x'
        assert bsg.y == 'test_y'
        assert bsg.reset_event == None
        assert bsg.x_range == None
        assert bsg.y_range == None
        assert bsg.add_interaction == True
        assert bsg.color_palette == None
        assert bsg.aggregate_col == 'test_agg_col'
        assert bsg.aggregate_fn == 'count'
        assert bsg.point_size == 1
        assert bsg.point_shape == 'circle'
        assert bsg.pixel_shade_type == 'eq_hist'
        assert bsg.pixel_density == 0.5
        assert bsg.pixel_spread == 'dynspread'
        assert bsg.width == 800
        assert bsg.height == 400
        assert bsg.tile_provider == 'CARTODBPOSITRON'
        assert bsg.library_specific_params == {}

        bsg1 = BaseScatterGeo(x='test_x', y='test_y')
        assert bsg1.aggregate_col == 'test_y'
