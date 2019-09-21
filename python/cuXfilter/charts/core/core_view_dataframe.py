import numpy as np
from typing import Dict
import panel as pn

from .core_chart import BaseChart

css = '''
.dataframe table{
  border: none;
}

.panel-df table{
    width: 100%; 
    border-collapse: collapse;
    border: none;
}
.panel-df td{
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
'''

pn.extension(raw_css=[css])


class ViewDataFrame:
    chart_type: str = 'view_dataframe'
    _height: int = 0
    columns = None
    _width: int = 0
    chart = None
    source = None
    use_data_tiles = False


    def __init__(self, columns=None, width=400, height=400):
        self.columns = columns
        self._width = width
        self._height = height

    @property
    def name(self):
        return self.chart_type

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        if self.chart is not None:
            self.update_dimensions(width=value)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if self.chart is not None:
            self.update_dimensions(height=value)


    def initiate_chart(self, dashboard_cls):
        self.generate_chart(dashboard_cls._data)

    def generate_chart(self, data):
        if self.columns is None:
            self.columns = list(data.columns)
        self.chart = pn.Column(pn.pane.HTML(data[self.columns], style={'width':'100%', 'height':'100%', 'overflow-y':'hidden', 'font-size':'0.5vw','overflow-x':'auto'}), css_classes=['panel-df'])
        self.chart.sizing_mode = 'scale_both'

    def view(self):
        return self.chart

    def reload_chart(self, data, patch_update:bool):
        self.chart[0].object = data[self.columns]

    def update_dimensions(self, width=None, height=None):
        """
                
        Parameters
        ----------

        

        Ouput
        -----
        """
        if width is not None:
            self.chart.width = width
        if height is not None:
            self.chart.height = height

    def query_chart_by_range(self, active_chart:BaseChart, query_tuple, data):
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
        self.reload_chart(data.query(str(min_val)+"<="+active_chart.x+"<="+str(max_val)), False)

    def query_chart_by_indices(self, active_chart:BaseChart, old_indices, new_indices, data):
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
            self.reload_chart(data, False)
        elif len(new_indices) == 1:
            #just a single index
            self.reload_chart(data.query(active_chart.x+"=="+str(float(new_indices[0]))), False)
        else:
            new_indices_str = ','.join(map(str,new_indices))
            self.reload_chart(data.query(active_chart.x+" in ("+new_indices_str+")"), False)
