from typing import Type, Dict
import numpy as np

from .core_aggregate import BaseAggregateChart
from ....assets.numba_kernels import calc_value_counts, calc_groupby
from ....datatile import DataTile
from ....layouts import chart_view
from ....assets import geo_json_mapper

class BaseChoropleth(BaseAggregateChart):

    chart_type: str = 'choropleth'
    reset_event = None
    _datatile_loaded_state: bool = False
    geo_mapper: Dict[str, str] = {}
    nan_color = 'white'
    use_data_tiles = True
    
    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        # if self.add_interaction:
        #     if state:
        #         self.filter_widget.bar_color = '#8ab4f7'
        #     else:
        #         self.filter_widget.bar_color = '#d3d9e2'

    def __init__(self, x, y=None, data_points=100, add_interaction=True, aggregate_fn='count', width=800, height=400, step_size=None, step_size_type=int, geoJSONSource=None, geoJSONProperty=None, geo_color_palette=None, **library_specific_params):
        '''
        Description:
        
        -------------------------------------------
        Input:
            x
            geoJSONSource
            geoJSONProperty
            y
            data_points
            add_interaction 
            geo_color_palette
            aggregate_fn
            width
            height
            step_size
            step_size_type
            nan_color
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

        if geoJSONSource is None:
            print("geoJSONSource is required for the choropleth map")
        else:
            self.geoJSONSource = geoJSONSource
            
        self.geo_color_palette = geo_color_palette
        self.geoJSONProperty = geoJSONProperty
        self.geo_mapper = geo_json_mapper(self.geoJSONSource, self.geoJSONProperty)
        self.height = height
        self.width = width

        self.stride = step_size
        self.stride_type = step_size_type

        self.library_specific_params = library_specific_params
        if 'nan_color' in self.library_specific_params:
            self.nan_color = self.library_specific_params['nan_color']
            self.library_specific_params.pop('nan_color')
        

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
            self.stride = self.stride_type( (self.max_value - self.min_value)/self.data_points )

        self.calculate_source(dashboard_cls._data)
        self.generate_chart()
        self.apply_mappers()

        self.add_events(dashboard_cls)
    
    def view(self):
        return chart_view(self.chart, width=self.width)

    def calculate_source(self, data, patch_update=False):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.y == self.x or self.y is None: 
            # it's a histogram
            df = calc_value_counts(data[self.x].to_gpu_array(), self.data_points)
        else:
            df = calc_groupby(self, data)

        dict_temp = {'X':list(df[0].astype(df[0].dtype)), 'Y':list(df[1].astype(df[1].dtype))}
        
        self.format_source_data(dict_temp, patch_update)
        
        
    def get_selection_callback(self, dashboard_cls):
        '''
        Description: generate callback for choropleth selection evetn
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def selection_callback(old, new):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices(old, new)

        return selection_callback

    def compute_query_dict(self, query_str_dict):
        '''
        Description: 

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        '''
        list_of_indices = self.get_selected_indices()
        if len(list_of_indices) == 0 or list_of_indices == ['']:
            query_str_dict.pop(self.name, None)
        elif len(list_of_indices) == 1:
            query_str_dict[self.name] = self.x+"=="+str(list_of_indices[0])
        else:
            indices_string = ",".join(map(str, list_of_indices))
            query_str_dict[self.name] = self.x+" in ("+indices_string+")"

       
    def add_events(self, dashboard_cls):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.add_interaction:
            self.add_selection_event(self.get_selection_callback(dashboard_cls))
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
            if dashboard_cls._active_view != self.name:
                #reset previous active view and set current chart as active view
                dashboard_cls._reset_current_view(new_active_view=self)
            dashboard_cls._reload_charts()        

        #add callback to reset chart button
        self.add_event(self.reset_event,reset_callback)

    def get_selected_indices(self):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        print('function to be overridden by library specific extensions')
        return []

    def add_selection_event(self, callback):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''

        print('function to be overridden by library specific extensions')