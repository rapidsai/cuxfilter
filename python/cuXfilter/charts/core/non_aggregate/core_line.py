from typing import Type, Dict
import numpy as np
import panel as pn

from .core_non_aggregate import BaseNonAggregate
from ....layouts import chart_view

class BaseLine(BaseNonAggregate):

    chart_type: str = 'line'
    stride = 0.0
    reset_event = None
    _datatile_loaded_state: bool = False
    filter_widget = None
    
    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if self.add_interaction:
            if state:
                self.filter_widget.bar_color = '#8ab4f7'
            else:
                self.filter_widget.bar_color = '#d3d9e2'

    def __init__(self, x, y=None, data_points=100, add_interaction=True, aggregate_fn='count', pixel_shade_type='linear',  width=400, height=400, step_size=None, step_size_type=int,  **library_specific_params):
        '''
        Description:
        
        -------------------------------------------
        Input:
            x
            y
            data_points
            add_interaction 
            aggregate_fn
            width
            height
            step_size
            step_size_type
            x_label_map
            y_label_map
            **library_specific_params
        -------------------------------------------

        Ouput:

        '''
        self.x = x
        self.y = y
        self.data_points = data_points
        self.add_interaction = add_interaction
        self.aggregate_fn = aggregate_fn
        self.height = height
        self.width = width
        self.stride = step_size
        self.stride_type = step_size_type
        self.pixel_shade_type = pixel_shade_type
        self.library_specific_params = library_specific_params

    def initiate_chart(self, dashboard_cls):
        '''
        Description:
        
        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        '''
        self.min_value = dashboard_cls._data[self.x].min()
        self.max_value = dashboard_cls._data[self.x].max()
        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type( (self.max_value - self.min_value)/self.data_points)

        self.calculate_source(dashboard_cls._data)
        self.generate_chart()
        self.apply_mappers()

        if self.add_interaction: self.add_range_slider_filter(dashboard_cls)
        self.add_events(dashboard_cls)
    
    def view(self):
        return chart_view(self.chart, self.filter_widget, width=self.width)
        
        
    def add_range_slider_filter(self, dashboard_cls):
        '''
        Description: add range slider to the bottom of the chart, for the filter function
                    to facilitate interaction behavior, that updates the rest of the charts on the page, using datatiles
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.stride is None:
            self.stride = self.stride_type( (self.max_value - self.min_value)/self.data_points )
        
        self.filter_widget = pn.widgets.RangeSlider(start=self.min_value, end=self.max_value, value=(self.min_value, self.max_value), step=self.stride, **{'width': self.width}, sizing_mode='scale_width')

        def filter_widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles()

            dashboard_cls._query_datatiles_by_range(event.new)

        #add callback to filter_Widget on value change
        self.filter_widget.param.watch(filter_widget_callback, ['value'], onlychanged=False)

    def compute_query_dict(self, query_str_dict):
        '''
        Description: 

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        '''
        
        if self.filter_widget.value != (self.filter_widget.start,self.filter_widget.end):
            min_temp,max_temp = self.filter_widget.value
            query_str_dict[self.name] =  str(min_temp)+'<='+str(self.x)+"<="+str(max_temp)
       
    def add_events(self, dashboard_cls):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.reset_event is not None:
            self.add_reset_event(dashboard_cls)



    def add_reset_event(self, dashboard_cls):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def reset_callback(event):
            self.filter_widget.value = (self.filter_widget.start, self.filter_widget.end)        

        #add callback to reset chart button
        self.add_event(self.reset_event,reset_callback)