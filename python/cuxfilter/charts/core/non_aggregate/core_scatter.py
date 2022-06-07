from typing import Tuple

from .core_non_aggregate import BaseNonAggregate
from ...constants import CUXF_DEFAULT_COLOR_PALETTE


class BaseScatter(BaseNonAggregate):
    """
    .. note::
        Non-aggregate charts do not support Datatiles

    """

    reset_event = None
    x_range: Tuple = None
    y_range: Tuple = None
    aggregate_col = None
    default_palette = CUXF_DEFAULT_COLOR_PALETTE

    @property
    def colors_set(self):
        return self._color_palette_input is not None

    @property
    def color_palette(self):
        if self.colors_set:
            return list(self._color_palette_input)
        return self.default_palette

    def __init__(
        self,
        x,
        y,
        x_range=None,
        y_range=None,
        add_interaction=True,
        color_palette=None,
        aggregate_col=None,
        aggregate_fn="count",
        point_size=1,
        point_shape="circle",
        pixel_shade_type="eq_hist",
        pixel_density=0.5,
        pixel_spread="dynspread",
        width=800,
        height=400,
        tile_provider=None,
        title="",
        timeout=100,
        legend=True,
        legend_position="center",
        unselected_alpha=0.2,
        **library_specific_params,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            x
            y
            x_range
            y_range
            add_interaction
            color_palette
            aggregate_col
            aggregate_fn
            point_size
            point_shape
            pixel_shade_type
            pixel_density
            pixel_spread
            width
            height
            title
            timeout
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = x
        self.y = y
        self.x_range = x_range
        self.y_range = y_range
        self.add_interaction = add_interaction
        self.aggregate_col = aggregate_col or y
        self._color_palette_input = color_palette
        self.aggregate_fn = aggregate_fn
        self.width = width
        self.height = height
        self.tile_provider = tile_provider
        self.point_shape = point_shape
        self.point_size = point_size
        self.title = title
        self.timeout = timeout
        self.pixel_shade_type = pixel_shade_type
        self.pixel_density = pixel_density
        self.pixel_spread = pixel_spread
        self.legend = legend
        self.legend_position = legend_position
        self.unselected_alpha = unselected_alpha
        self.library_specific_params = library_specific_params
