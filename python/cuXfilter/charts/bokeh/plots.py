from ..core.aggregate import BaseBar, BaseChoropleth, BaseLine, BaseDataSizeIndicator

import pandas as pd
import numpy as np
from typing import Type
from bokeh import events
from bokeh.plotting import figure
import bokeh
from bokeh.models.annotations import Title
from bokeh.models import ColumnDataSource, LinearColorMapper, LogColorMapper, ColorBar, BasicTicker, PrintfTickFormatter, HoverTool, BoxSelectTool

class Bar(BaseBar):
    """
        Description:
    """
    reset_event = events.Reset
    data_y_axis = 'top'
    data_x_axis = 'x'
    

    def format_source_data(self, source_dict, patch_update=False):
        """
        Description:
            format source
        
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        

        Ouput:
        """
        range_x_origin = [round(x,4) for x in source_dict['X']]
        range_x = []
        
        if self.max_value < 1:
            """
            handling labels in bokeh plots when max value is under 1
            """
            range_x = [int(x*100)  for x in range_x_origin]
            if self.x_label_map is None:
                temp_mapper_index = list(range(int(round(self.min_value)),int(round(self.max_value))*100+1))
                temp_mapper_value = [str(x/100) for x in temp_mapper_index]
                self.x_label_map = dict(zip(temp_mapper_index, temp_mapper_value))
        else:
            range_x = range_x_origin
        
        if patch_update == False:
            self.source = ColumnDataSource(dict(x=np.array(range_x), top=np.array(source_dict['Y'])))
            self.source_backup = self.source.to_df()
        else:
            patch_dict = {
                            self.data_y_axis: [(slice(len(source_dict['Y'])), np.array(source_dict['Y']))],
                     }
            self.source.patch(patch_dict)

    def get_source_y_axis(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if self.source is not None:
            return self.source.data[self.data_y_axis] #return list
        return self.source
            
    def generate_chart(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        self.chart = figure(title=self.x, tools="pan, wheel_zoom, reset", active_scroll='wheel_zoom', active_drag='pan')
        self.chart.vbar(x=self.data_x_axis, top=self.data_y_axis, width=0.9, source = self.source, color=self.color)
        # self.chart.toolbar.active_drag = 'auto'
        # self.chart.toolbar.active_scroll = 'auto'


    def update_dimensions(self, width=None, height=None):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def apply_mappers(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if self.x_label_map is not None:
            self.chart.xaxis.major_label_overrides = self.x_label_map
        if self.y_label_map is not None:
            self.chart.yaxis.major_label_overrides = self.y_label_map

    def reload_chart(self, data, patch_update=True):
        """
        Description: 

        
        Input:

        

        Ouput:
        """
        self.calculate_source(data, patch_update=patch_update)
    

    def reset_chart(self, data:np.array=np.array([])):
        """
        Description: 
            if len(data) is 0, reset the chart using self.source_backup
        
        Input:
        data = list() --> update self.data_y_axis in self.source
        

        Ouput:
        """
        if data.size == 0:
            data = self.source_backup[self.data_y_axis] #np array
        
        #verifying length is same as x axis
        x_axis_len = self.source.data[self.data_x_axis].size
        data = data[:x_axis_len]

        patch_dict = {
                            self.data_y_axis: [(slice(data.size), data)],
                     }
        self.source.patch(patch_dict)

class Line(BaseLine):
    """
        Description:
    """
    reset_event = events.Reset
    data_y_axis = 'y'
    data_x_axis = 'x'


    def format_source_data(self, source_dict, patch_update=False):
        """
        Description:
            format source
        
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        

        Ouput:
        """
        range_x_origin = [round(x,4) for x in source_dict['X']]
        range_x = []
        
        if self.max_value < 1:
            """
            handling labels in bokeh plots when max value is under 1
            """
            range_x = [int(x*100)  for x in range_x_origin]
            if self.x_label_map is None:
                temp_mapper_index = list(range(int(round(self.min_value)),int(round(self.max_value))*100+1))
                temp_mapper_value = [str(x/100) for x in temp_mapper_index]
                self.x_label_map = dict(zip(temp_mapper_index, temp_mapper_value))
        else:
            range_x = range_x_origin
        
        if patch_update == False:
            self.source = ColumnDataSource(dict(x=np.array(range_x), y=np.array(source_dict['Y'])))
            self.source_backup = self.source.to_df()
        else:
            patch_dict = {
                            self.data_y_axis: [(slice(len(source_dict['Y'])), np.array(source_dict['Y']))],
                     }
            self.source.patch(patch_dict)

    def get_source_y_axis(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if self.source is not None:
            return self.source.data[self.data_y_axis] #return list
        return self.source
            
    def generate_chart(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """

        self.chart = figure(title=self.x, tools=" pan, wheel_zoom, reset", active_scroll='wheel_zoom', active_drag='pan')
        self.chart.line(x=self.data_x_axis, y=self.data_y_axis, source = self.source, color=self.color)

    def update_dimensions(self, width=None, height=None):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height


    def apply_mappers(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if self.x_label_map is not None:
            self.chart.xaxis.major_label_overrides = self.x_label_map
        if self.y_label_map is not None:
            self.chart.yaxis.major_label_overrides = self.y_label_map

    def reload_chart(self, data, patch_update=True):
        """
        Description: 

        
        Input:

        

        Ouput:
        """
        self.calculate_source(data, patch_update=patch_update)


    def reset_chart(self, data:np.array=np.array([])):
        """
        Description: 
            if len(data) is 0, reset the chart using self.source_backup
        
        Input:
        data = list() --> update self.data_y_axis in self.source
        

        Ouput:
        """
        if data.size == 0:
            data = self.source_backup[self.data_y_axis] #np array
        
        #verifying length is same as x axis
        x_axis_len = self.source.data[self.data_x_axis].size
        data = data[:x_axis_len]

        patch_dict = {
                            self.data_y_axis: [(slice(data.size), data)],
                     }
        self.source.patch(patch_dict)


class Choropleth(BaseChoropleth):
    reset_event = None #reset event handling not required, as the default behavior unselects all selected points, and that is already taken care of
    data_y_axis = 'rates'
    data_x_axis = 'x'

    def format_source_data(self, source_dict, patch_update= False):
        """format source

        Parameters:
        ---
        source_dict : {
            'X': [],
            'Y': []
        }
        

        Ouput:
        ---
        """
        self.source: Type[ColumnDataSource]

        res_df = pd.DataFrame(source_dict)
        

        if patch_update == False:
            lats = []
            longs = []
            rates = []
            prop = []
            for i in self.geo_mapper:
                for polygon in self.geo_mapper[i]:
                    lat, long = np.array(polygon[0]).T.tolist()
                    prop.append(i)
                    lats.append(lat)
                    longs.append(long)
                    if i in source_dict['X']:
                        rates.append(res_df.loc[res_df['X'] == i, 'Y'].iloc[0])
                    else:
                        rates.append(np.nan)
            rates = np.array(rates)

            self.source = ColumnDataSource({self.data_x_axis:np.array([]), 'xs':np.array([]), 'ys':np.array([]), self.data_y_axis:np.array([])})
            data = {
                self.data_x_axis:np.array(prop),
                'xs':np.array(lats), 'ys':np.array(longs),
                self.data_y_axis:rates
                }
            self.source.stream(data)

        else:
            rates = []
            for i in source_dict['X']:
                if i in self.geo_mapper:
                    temp_list = [res_df.loc[res_df['X'] == float(i), 'Y'].iloc[0]]*len(self.geo_mapper[i])
                    rates = rates+temp_list
            rates = np.array(rates)
            patch_dict = {
                                self.data_y_axis: [(slice(len(rates)), rates)],
                        }
            self.source.patch(patch_dict)

    def get_source_y_axis(self):
        """
        Parameters:
        ---
        

        Ouput:
        ---
        """
        if self.source is not None:
            unique_x_axis = np.unique(self.source.data[self.data_x_axis]).tolist()
            # unique_y_axis = .unique(self.source.data[self.data_y_axis])
            return_val = np.zeros(self.data_points)
            for index, x in enumerate(unique_x_axis):
                return_val[int(x)] = self.source.data[self.data_y_axis][int(x)]
            return  return_val#return np array
        return self.source
            
    def generate_chart(self):
        """
        Parameters:
        ---
        

        Ouput:
        ---
        """
        if self.geo_color_palette is None:
            self.geo_color_palette = bokeh.palettes.Purples9

        mapper = LinearColorMapper(palette=self.geo_color_palette, nan_color=self.nan_color, low=np.nanmin(self.source.data[self.data_y_axis]),high=np.nanmax(self.source.data[self.data_y_axis]))

        tooltips_r = [
            (self.x,"@"+self.data_x_axis),
            (self.data_y_axis, "@"+self.data_y_axis)
        ]

        self.chart = figure(title="Geo Map for "+self.name, toolbar_location="left", tooltips=tooltips_r, tools="hover, pan, wheel_zoom, tap, reset",
                            active_scroll='wheel_zoom', active_drag='pan',
                           **self.library_specific_params)

        patch = self.chart.patches(xs='xs', ys='ys',source=self.source,
                        fill_color={'field':self.data_y_axis, 'transform':mapper})


        color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="7pt",
                            ticker=BasicTicker(desired_num_ticks=10),
                            formatter=PrintfTickFormatter(format="%f"),
                            label_standoff=6, border_line_color=None, location=(0, 0))
        
        self.chart.add_layout(color_bar, 'left')
        
        self.source = patch.data_source
        self.source_backup = self.source.data.copy()

    def update_dimensions(self, width=None, height=None):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height


    def apply_mappers(self):
        """
        Parameters:
        ---
        

        Ouput:
        ---
        """
        if self.x_label_map is not None:
            self.chart.xaxis.major_label_overrides = self.x_label_map
        if self.y_label_map is not None:
            self.chart.yaxis.major_label_overrides = self.y_label_map

    def reload_chart(self, data, patch_update=True):
        """
        Parameters:
        ---
        

        Ouput:
        ---
        """
        self.calculate_source(data, patch_update=patch_update)
    

    def reset_chart(self, data:np.array = np.array([])):
        """if len(data) is 0, reset the chart using self.source_backup

        Parameters:
        ---
        data:  list()
            update self.data_y_axis in self.source

        Ouput:
        ---

        """
        if data.size == 0:
            data = self.source_backup[self.data_y_axis].tolist()
        
        #verifying length is same as x axis
        x_axis_len = self.source.data[self.data_x_axis].size
        data = data[:x_axis_len]

        rates = []
        for i in range(data.size):
            if i in self.geo_mapper:
                temp_list = [data[i]]*len(self.geo_mapper[i])
                rates = rates+temp_list
        rates = np.array(rates)
        patch_dict = {
                            self.data_y_axis: [(slice(len(rates)), rates)],
                     }

        self.source.patch(patch_dict)

    def map_indices_to_values(self, indices:list):
        """
        Parameters:
        ---
        

        Ouput:
        ---
        """
        list_final = []
        for n in indices:
            list_final.append(int(self.source.data[self.data_x_axis][n]))
        return list_final

    def get_selected_indices(self):
        """
        Parameters:
        ---
        

        Ouput:
        ---
        """
        return self.map_indices_to_values(self.source.selected.indices)

    def add_selection_event(self, callback):
        """
        Parameters:
        ---
        

        Ouput:
        ---
        """
        def temp_callback(attr, old, new):
            old = self.map_indices_to_values(old)
            new = self.map_indices_to_values(new)
            callback(old, new)
        
        self.source.selected.on_change('indices', temp_callback)


class DataSizeIndicator(BaseDataSizeIndicator):
    """
        Description:
    """
    data_y_axis = 'right'
    data_x_axis = 'y'


    def format_source_data(self, source_dict, patch_update=False):
        """
        Description:
            format source
        
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        

        Ouput:
        """
        if patch_update == False:
            self.source = ColumnDataSource({self.data_x_axis:np.array(source_dict['X']), self.data_y_axis:np.array(source_dict['Y'])})
            self.source_backup = self.source.to_df()
        else:
            patch_dict = {
                            self.data_y_axis: [(slice(len(source_dict['Y'])), np.array(source_dict['Y']))],
                     }
            self.source.patch(patch_dict)

    def get_source_y_axis(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if self.source is not None:
            return self.source.data[self.data_y_axis] #return list
        return self.source
            
    def generate_chart(self):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        self.chart = figure(height=20, x_range=(0,self.max_value), tools="")
        self.chart.hbar(right=self.data_y_axis, y=self.data_x_axis, height=2.0, source = self.source)
        self.chart.yaxis.visible = False
        self.chart.xaxis.visible = False
        self.chart.ygrid.visible = False
        self.chart.xgrid.visible = False
        self.chart.toolbar.logo = None
    
    def update_dimensions(self, width=None, height=None):
        """
        Description:

        
        Input:

        

        Ouput:
        """
        if width is not None:
            self.chart.plot_width = width
        if height is not None:
            self.chart.plot_height = height

    def reload_chart(self, data):
        """
        Description: 

        
        Input:

        

        Ouput:
        """
        self.calculate_source(data, patch_update=True)
        self.update_title()

    def update_title(self):
        """
        Description: 

        
        Input:

        

        Ouput:
        """
        self.data_points_label.object = '<b> Points Selected: '+str(self.get_source_y_axis()[0])
        # t = Title()
        # t.text = 'Points Selected: '+str(self.get_source_y_axis()[0])
        # # self.chart.title = t
        # self.chart.js_link('value', self.chart.title, t)

    def reset_chart(self, data:np.array=np.array([])):
        """
        Description: 
            if len(data) is 0, reset the chart using self.source_backup
        
        Input:
        data = list() --> update self.data_y_axis in self.source
        

        Ouput:
        """
        if data.size == 0:
            data = self.source_backup[self.data_y_axis] #np array
        
        #verifying length is same as x axis
        x_axis_len = self.source.data[self.data_x_axis].size
        data = data[:x_axis_len]

        patch_dict = {
                            self.data_y_axis: [(slice(data.size), data)],
                     }
        self.source.patch(patch_dict)
        self.update_title()