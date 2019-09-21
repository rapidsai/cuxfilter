from ..core import BaseWidget
from ..core.aggregate import BaseDataSizeIndicator
from ...assets.numba_kernels import aggregated_column_unique

import panel as pn
import datetime as dt
import numpy as np


class RangeSlider(BaseWidget):
    chart_type: str = 'widget_range_slider'
    _datatile_loaded_state: bool = False


    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = '#8ab4f7'
        else:
            self.chart.bar_color = '#d3d9e2'

    
    def initiate_chart(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.min_value = dashboard_cls._data[self.x].min()
        self.max_value = dashboard_cls._data[self.x].max()
        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type((self.max_value - self.min_value) / self.data_points)
        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.chart = pn.widgets.RangeSlider(name=self.x, start=self.min_value, end=self.max_value, value=(self.min_value, self.max_value), step=self.stride, width=self.width, height=self.height, **self.params)


    
    def add_events(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles()

            dashboard_cls._query_datatiles_by_range(event.new)

        #add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ['value'], onlychanged=False)
        # self.add_reset_event(dashboard_cls)
    
    def compute_query_dict(self, query_str_dict):
        '''
        Description: 

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        '''
        
        if self.chart.value != (self.chart.start,self.chart.end):
            min_temp, max_temp = self.chart.value
            query_str_dict[self.name] =  str(min_temp)+'<='+str(self.x)+"<="+str(max_temp)


class IntSlider(BaseWidget):
    chart_type: str = 'widget_int_slider'
    _datatile_loaded_state: bool = False
    value = None

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = '#8ab4f7'
        else:
            self.chart.bar_color = '#d3d9e2'

    
    def initiate_chart(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.min_value = int(dashboard_cls._data[self.x].min())
        self.max_value = int(dashboard_cls._data[self.x].max())
        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type( (self.max_value - self.min_value) / self.data_points)
        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.value is None:
            self.value = self.min_value 
        self.chart = pn.widgets.IntSlider(name=self.x, start=self.min_value, end=self.max_value, value=self.value, step=self.stride, width=self.width, height=self.height, **self.params)


    
    def add_events(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)

            dashboard_cls._query_datatiles_by_indices([event.old], [event.new])

        #add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ['value'], onlychanged=False)
        # self.add_reset_event(dashboard_cls)
    
    def compute_query_dict(self, query_str_dict):
        '''
        Description: 

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        '''
        
        query_str_dict[self.name] =  str(self.x)+"=="+str(self.chart.value)


class FloatSlider(BaseWidget):
    chart_type: str = 'widget_float_slider'
    _datatile_loaded_state: bool = False
    value = None

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = '#8ab4f7'
        else:
            self.chart.bar_color = '#d3d9e2'
    
    def initiate_chart(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.min_value = dashboard_cls._data[self.x].min()
        self.max_value = dashboard_cls._data[self.x].max()
        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type( (self.max_value - self.min_value) / self.data_points)
        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.value is None:
            self.value = self.min_value 
        self.chart = pn.widgets.FloatSlider(name=self.x, start=self.min_value, end=self.max_value, value=self.value, step=self.stride, width=self.width, height=self.height, **self.params)


    
    def add_events(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)

            dashboard_cls._query_datatiles_by_indices([event.old], [event.new])

        #add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ['value'], onlychanged=False)
        # self.add_reset_event(dashboard_cls)
    
    def compute_query_dict(self, query_str_dict):
        '''
        Description: 

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        '''
        
        query_str_dict[self.name] =  str(self.x)+"=="+str(self.chart.value)


class DropDown(BaseWidget):
    chart_type: str = 'widget_dropdown'
    _datatile_loaded_state: bool = False
    value = None

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.color = '#8ab4f7'
        else:
            self.chart.color = '#d3d9e2'

    def initiate_chart(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.min_value = dashboard_cls._data[self.x].min()
        self.max_value = dashboard_cls._data[self.x].max()

        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type( (self.max_value - self.min_value)/self.data_points)

        
        self.calc_list_of_values(dashboard_cls._data)

        self.generate_widget()
        
        self.add_events(dashboard_cls)


    def calc_list_of_values(self, data):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.label_map is None:
            self.list_of_values = data[self.x].unique().to_pandas().tolist()
            if len(self.list_of_values) > self.data_points:
                self.list_of_values = aggregated_column_unique(self, data)
            
            if len(self.list_of_values)>500:
                print('It is not recommended to use a column with so many different values for dropdown menu')
            self.list_of_values.append('')
            self.data_points = len(self.list_of_values) - 1
        else:
            self.list_of_values = self.label_map
            self.list_of_values[''] = ''
            self.data_points = len(self.list_of_values.items()) - 1

        self.data_points = len(self.list_of_values) - 1

    def generate_widget(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.chart = pn.widgets.Select(name=self.x, options=self.list_of_values, value='', width=self.width, height=self.height, **self.params)


    
    def add_events(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices([], [event.new])

        #add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ['value'], onlychanged=False)
        # self.add_reset_event(dashboard_cls)
    
    def compute_query_dict(self, query_str_dict):
        '''
        Description: 

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        '''
        if len(str(self.chart.value)) > 0:
            query_str_dict[self.name] =  str(self.x)+"=="+str(self.chart.value)



class MultiSelect(BaseWidget):
    chart_type: str = 'widget_multi_select'
    _datatile_loaded_state: bool = False
    value = None

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.color = '#8ab4f7'
        else:
            self.chart.color = '#d3d9e2'

    def initiate_chart(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.min_value = dashboard_cls._data[self.x].min()
        self.max_value = dashboard_cls._data[self.x].max()

        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type(1)
        
        self.calc_list_of_values(dashboard_cls._data)

        self.generate_widget()
        
        self.add_events(dashboard_cls)


    def calc_list_of_values(self, data):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.label_map is None:
            self.list_of_values = data[self.x].unique().to_pandas().tolist()
            # if len(self.list_of_values) > self.data_points:
            #     self.list_of_values = aggregated_column_unique(self, data)
            
            if len(self.list_of_values)>500:
                print('It is not recommended to use a column with so many different values for dropdown menu')
            self.list_of_values.append('')
            self.data_points = len(self.list_of_values) - 1
        else:
            self.list_of_values = self.label_map
            self.list_of_values[''] = ''
            self.data_points = len(self.list_of_values.items()) - 1

    def generate_widget(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''

        self.chart = pn.widgets.MultiSelect(name=self.x, options=self.list_of_values, value=[''], width=self.width, height=self.height, **self.params)


    
    def add_events(self, dashboard_cls):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices(event.old, event.new)

        #add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ['value'], onlychanged=False)
        # self.add_reset_event(dashboard_cls)
    
    def compute_query_dict(self, query_str_dict):
        '''
        Description: 

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        '''
        if len(self.chart.value) == 0 or self.chart.value == ['']:
            query_str_dict.pop(self.name, None)
        elif len(self.chart.value) == 1:
            query_str_dict[self.name] = self.x+"=="+str(self.chart.value[0])
        else:
            indices_string = ",".join(map(str, self.chart.value))
            query_str_dict[self.name] = self.x+" in ("+indices_string+")"


class DataSizeIndicator(BaseDataSizeIndicator):
    '''
        Description:
    '''

    css = '''
        .non-handle-temp .bk-noUi-origin {
        visibility: hidden;
        color:blue;
        }

        .non-handle-temp [disabled] .bk-noUi-connect {
            background: purple; 
        }
        '''
    pn.extension(raw_css=[css])    

    def format_source_data(self, source_dict, patch_update=False):
        '''
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        '''
        if patch_update:
            self.chart.value = float(source_dict['Y'][0])
        else:        
            self.source = float(source_dict['Y'][0])
            self.source_backup = self.source

    def get_source_y_axis(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        return self.chart.value
            
    def generate_chart(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.chart = pn.widgets.FloatSlider(name='Data Points selected', width=self.width, start=0, end=self.max_value, value=self.max_value)
        self.chart.bar_color = '#5742f5'

    def reload_chart(self, data, patch_update=True):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.calculate_source(data, patch_update=patch_update)

    def reset_chart(self, data:float=-1):
        '''
        Description: 
            if len(data) is 0, reset the chart using self.source_backup
        -------------------------------------------
        Input:
        data = list() --> update self.data_y_axis in self.source
        -------------------------------------------

        Ouput:
        '''
        if data == -1:
            self.chart.value = self.source_backup #float
        else:
            self.chart.value = float(data)