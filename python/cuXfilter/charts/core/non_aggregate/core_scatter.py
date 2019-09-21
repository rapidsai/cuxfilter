from typing import Type, Dict, Tuple
import numpy as np

from .core_non_aggregate import BaseNonAggregate
from ....layouts import chart_view

class BaseScatter(BaseNonAggregate):
    '''
        No datatiles support in scatter plot charts

        If dataset size is greater than a few thousand points, scatter geos can crash the browser tabs,
        and is only recommended with cudatashader plugin, in which case an image is rendered instead of points on canvase
    '''
    chart_type: str = 'scatter'
    stride = float
    reset_event = None
    x_range: Tuple = None
    y_range: Tuple = None
    aggregate_col = None

    def __init__(self, x, y, x_range=None, y_range=None, add_interaction=True, color_palette=None, aggregate_col=None, aggregate_fn='count',point_size=1, point_shape='circle', pixel_shade_type='eq_hist',pixel_density=0.5, pixel_spread='dynspread',  width=800, height=400, **library_specific_params):
        '''
        Description:
        
        -------------------------------------------
        Input:
            x
            y
            x_range
            y_range
            add_interaction 
            geo_color_palette
            aggregate_col
            aggregate_fn
            width
            height
            tile_provider
            **library_specific_params
        -------------------------------------------

        Ouput:

        '''
        self.x = x
        self.y = y
        self.x_range = x_range
        self.y_range = y_range
        self.add_interaction = add_interaction

        if aggregate_col is not None:
            self.aggregate_col = aggregate_col
        else:
            self.aggregate_col = self.y

        self.color_palette = color_palette
        self.aggregate_fn = aggregate_fn
        self.width = width
        self.height = height
        self.point_shape = point_shape
        self.point_size = point_size
        self.pixel_shade_type = pixel_shade_type
        self.pixel_density = pixel_density
        self.pixel_spread = pixel_spread
        self.library_specific_params = library_specific_params