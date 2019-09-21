from typing import Type, Dict, Tuple
import numpy as np

from ..core_chart import BaseChart
from ....layouts import chart_view

class BaseNonAggregate(BaseChart):
    '''
        No datatiles support in non_data_tiles plot charts

        If dataset size is greater than a few thousand points, scatter geos can crash the browser tabs,
        and is only recommended with cudatashader plugin, in which case an image is rendered instead of points on canvase
    '''
    reset_event = None
    x_range: Tuple = None
    y_range: Tuple = None
    aggregate_col = None
    use_data_tiles = False
    
    
    def initiate_chart(self, dashboard_cls):
        '''
        Description:
        
        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        '''
        if self.x_range is None:
            self.x_range = (dashboard_cls._data[self.x].min(), dashboard_cls._data[self.x].max())
        if self.y_range is None:
            self.y_range = (dashboard_cls._data[self.y].min(), dashboard_cls._data[self.y].max())
        self.calculate_source(dashboard_cls._data)
        self.generate_chart()
        self.add_events(dashboard_cls)
    
    def view(self):
        return chart_view(self.chart, width = self.width)

    def calculate_source(self, data):
        '''
        Description:
        
        -------------------------------------------
        Input:
        data = cudf.DataFrame
        -------------------------------------------

        Ouput:
        '''
        self.format_source_data(data)
        
        
        
    def get_selection_geometry_callback(self, dashboard_cls):
        '''
        Description: generate callback for choropleth selection evetn
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:

        '''

        def selection_callback(xmin, xmax, ymin, ymax):
            if dashboard_cls._active_view != self.name:
                #reset previous active view and set current chart as active view
                dashboard_cls._reset_current_view(new_active_view=self)
                self.source = dashboard_cls._data
            
            self.x_range = (xmin, xmax)
            self.y_range = (ymin, ymax)
            
            dashboard_cls._query_str_dict[self.name] = str(xmin)+"<="+self.x+" <= "+str(xmax)+" and "+str(ymin)+"<="+self.y+" <= "+str(ymax)
            temp_data = dashboard_cls._query(dashboard_cls._query_str_dict[self.name])
            #reload all charts with new queried data (cudf.DataFrame only)
            dashboard_cls._reload_charts(data=temp_data, ignore_cols=[self.name])
            self.reload_chart(temp_data, False)
            del(temp_data)

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
        if self.x_range is not None and self.y_range is not None:
            query_str_dict[self.name] = str(self.x_range[0])+"<="+self.x+" <= "+str(self.x_range[1])+" and "+str(self.y_range[0])+"<="+self.y+" <= "+str(self.y_range[1])
       
    def add_events(self, dashboard_cls):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.add_interaction:
            self.add_selection_geometry_event(self.get_selection_geometry_callback(dashboard_cls))
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
                self.source = dashboard_cls._data
            self.x_range = None
            self.y_range = None
            dashboard_cls._reload_charts()         
        
        #add callback to reset chart button
        self.add_event(self.reset_event,reset_callback)


    def query_chart_by_range(self, active_chart:BaseChart, query_tuple, datatile=None):
        '''
        Description: 

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: None in case of Gpu Geo Scatter charts
        -------------------------------------------

        Ouput:
        '''
        min_val, max_val = query_tuple
        self.reload_chart(self.source.query(str(min_val)+"<="+active_chart.x+"<="+str(max_val)), False)

    def query_chart_by_indices(self, active_chart:BaseChart, old_indices, new_indices, datatile=None):
        '''
        Description: 

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: None in case of Gpu Geo Scatter charts
        -------------------------------------------

        Ouput:
        '''
        if '' in new_indices: new_indices.remove('') 
        if len(new_indices) == 0:
            #case: all selected indices were reset
            #reset the chart
            self.reload_chart(self.source, False)
        elif len(new_indices) == 1:
            #just a single index
            self.reload_chart(self.source.query(active_chart.x+"=="+str(float(new_indices[0]))), False)
        else:
            new_indices_str = ','.join(map(str,new_indices))
            self.reload_chart(self.source.query(active_chart.x+" in ("+new_indices_str+")"), False)


    def add_selection_geometry_event(self, callback):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''

        #('function to be overridden by library specific extensions')

    
    def reset_chart_geometry_ranges(self):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''

        #('function to be overridden by library specific extensions')