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

    def __init__(
        self,
        x,
        y,
        x_range=None,
        y_range=None,
        add_interaction=True,
        color_palette=CUXF_DEFAULT_COLOR_PALETTE,
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

        if aggregate_col is not None:
            self.aggregate_col = aggregate_col
        else:
            self.aggregate_col = self.y

        # if tuple, typecasting color_palette to a list
        self.color_palette = list(color_palette)
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
        self.library_specific_params = library_specific_params
