import pytest

from cuxfilter.charts.core.non_aggregate.core_scatter import BaseScatter
from cuxfilter.charts import constants

pytest


class TestBaseScatter:
    def test_variables(self):
        bs = BaseScatter(x="test_x", y="test_y", aggregate_col="test_agg_col")

        assert bs.chart_type is None
        assert bs.x == "test_x"
        assert bs.y == "test_y"
        assert bs.reset_event is None
        assert bs.x_range is None
        assert bs.y_range is None
        assert bs.add_interaction is True
        assert bs.color_palette == constants.CUXF_DEFAULT_COLOR_PALETTE
        assert bs.aggregate_col == "test_agg_col"
        assert bs.aggregate_fn == "count"
        assert bs.point_size == 1
        assert bs.point_shape == "circle"
        assert bs.pixel_shade_type == "eq_hist"
        assert bs.pixel_density == 0.5
        assert bs.pixel_spread == "dynspread"
        assert bs.width == 800
        assert bs.height == 400
        assert bs.library_specific_params == {}

        bs1 = BaseScatter(x="test_x", y="test_y")
        assert bs1.aggregate_col == "test_y"
