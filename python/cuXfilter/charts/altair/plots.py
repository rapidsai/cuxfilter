from ..core.aggregate import BaseBar

from typing import Type
# from bokeh import events
import pandas as pd
import altair as alt
import panel as pn

pn.extension('vega')
# alt.renderers.enable('notebook')

class Bar(BaseBar):
    reset_event = None
    data_y_axis = 'y'
    data_x_axis = 'x'
    
    def format_source_data(self, source_dict, patch_update= False):
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
        range_x = [round(x,4) for x in source_dict['X']]
        
        if self.max_value < 1:
            range_x = [x*100 for x in range_x]

        source_dict['X'] = range_x
        if not patch_update:
            self.source = pd.DataFrame({self.data_x_axis: source_dict['X'], self.data_y_axis: source_dict['Y']})
            self.source_backup = self.source.copy()
        else:
            self.source[self.data_y_axis] = source_dict['Y']

    def generate_chart(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.chart = pn.panel(alt.Chart(self.source).mark_bar().encode(x='x:Q', y='y:Q').properties(width=self.width, height=self.height, **self.library_specific_params))
        
        
    def reload_chart(self, data):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.calculate_source(data, patch_update=True)
        self.chart.param.trigger('object')
    

    def reset_chart(self, data:list=[]):
        '''
        Description: 
            if len(data) is 0, reset the chart using self.source_backup
        -------------------------------------------
        Input:
        data = list() --> update self.data_y_axis in self.source
        -------------------------------------------

        Ouput:
        '''
        if len(data) == 0:
            data = self.source_backup[self.data_y_axis].tolist()
        
        #verifying length is same as x axis
        data = data[:len(self.source[self.data_x_axis].tolist())]

        self.source[self.data_y_axis] = data
        self.chart.param.trigger('object')
        
class Line:
    name:str
class Scatter:
    name:str
class Choropleth:
    name:str