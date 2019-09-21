from ..core.non_aggregate import BaseScatterGeo, BaseScatter, BaseLine
from .custom_extensions import InteractiveImage

import cudatashader as cds
from cudatashader import transfer_functions as tf
from cudatashader.colors import Hot, Elevation
import pandas as pd
import numpy as np
from typing import Type
import re

from bokeh import events
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, BoxSelectTool
from bokeh.tile_providers import get_provider, Vendors

class ScatterGeo(BaseScatterGeo):
    '''
        Description:
    '''
    reset_event = events.Reset
    data_y_axis = 'y'
    data_x_axis = 'x'

        
    def format_source_data(self, data):
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
        self.source = data

    def generate_InteractiveImage_callback(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = cds.Canvas(plot_width=w, plot_height=h, x_range=x_range, y_range=y_range)
            agg = cvs.points(data_source, self.x, self.y, getattr(cds, self.aggregate_fn)(self.aggregate_col))
            img= tf.shade(agg, cmap=self.color_palette, how=self.pixel_shade_type)
            if self.pixel_spread == 'dynspread':
                return tf.dynspread(img, threshold=self.pixel_density, max_px=self.point_size, shape=self.point_shape)
            else:
                return tf.spread(img, px=self.point_size, shape=self.point_shape)
    
        return viewInteractiveImage
            
    def generate_chart(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.color_palette is None:
            self.color_palette = Hot
        
        if type(self.tile_provider) == str:
            self.tile_provider = get_provider(self.tile_provider)
        
        self.chart = figure(title="Geo Scatter plot for "+self.aggregate_fn, toolbar_location="right", tools="pan, wheel_zoom, reset", active_scroll='wheel_zoom', active_drag='pan',
                            x_range=self.x_range, y_range = self.y_range, width=self.width, height=self.height)

        self.chart.add_tools(BoxSelectTool())
        self.chart.add_tile(self.tile_provider)
        self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(self.chart, self.generate_InteractiveImage_callback(), data_source=self.source)
        
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


    def reload_chart(self, data, update_source=False):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if data is not None:        
            self.interactive_image.update_chart(data_source=data)
            if update_source:
                self.format_source_data(data)
        

    def reset_chart_geometry_ranges(self):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        # self.chart.x_range.start,self.chart.x_range.end = self.chart.x_range.reset_start,self.chart.x_range.reset_end
        # self.chart.y_range.start,self.chart.y_range.end = self.chart.y_range.reset_start,self.chart.y_range.reset_end
        # self.source = self.interactive_image.kwargs['data_source']

    def add_selection_geometry_event(self, callback):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def temp_callback(event):
            xmin, xmax, ymin, ymax = event.geometry['x0'], event.geometry['x1'],event.geometry['y0'],event.geometry['y1']
            callback(xmin, xmax, ymin, ymax)
        
        self.chart.on_event(events.SelectionGeometry, temp_callback)

class Scatter(BaseScatter):
    '''
        Description:
    '''
    reset_event = events.Reset
    data_y_axis = 'y'
    data_x_axis = 'x'


    def format_source_data(self, data):
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
        self.source = data
        
    def generate_InteractiveImage_callback(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = cds.Canvas(plot_width=w, plot_height=h, x_range=x_range, y_range=y_range)
            agg = cvs.points(data_source, self.x, self.y, getattr(cds, self.aggregate_fn)(self.aggregate_col))
            img= tf.shade(agg, cmap=self.color_palette, how=self.pixel_shade_type)
            if self.pixel_spread == 'dynspread':
                return tf.dynspread(img, threshold=self.pixel_density, max_px=self.point_size, shape=self.point_shape)
            else:
                return tf.spread(img, px=self.point_size, shape=self.point_shape)
    
        return viewInteractiveImage
            
    def generate_chart(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.color_palette is None:
            self.color_palette = Hot
        
        
        self.chart = figure(title="Geo Scatter plot for "+self.aggregate_fn, toolbar_location="right", tools="pan, wheel_zoom, reset", active_scroll='wheel_zoom', active_drag='pan',
                            x_range=self.x_range, y_range = self.y_range, width=self.width, height=self.height)

        self.chart.add_tools(BoxSelectTool())
        # self.chart.add_tile(self.tile_provider)
        # self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(self.chart, self.generate_InteractiveImage_callback(), data_source=self.source)
        
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

    def reload_chart(self, data, update_source=False):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if data is not None:        
            self.interactive_image.update_chart(data_source=data)
            if update_source:
                self.format_source_data(data)

    def reset_chart_geometry_ranges(self):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        # self.chart.x_range.start,self.chart.x_range.end = self.chart.x_range.reset_start,self.chart.x_range.reset_end
        # self.chart.y_range.start,self.chart.y_range.end = self.chart.y_range.reset_start,self.chart.y_range.reset_end
        # self.get_selection_geometry_callback()(self.chart.x_range.start,self.chart.x_range.end, self.chart.y_range.start,self.chart.y_range.end)
        # self.source = self.interactive_image.kwargs['data_source']

    def add_selection_geometry_event(self, callback):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def temp_callback(event):
            xmin, xmax, ymin, ymax = event.geometry['x0'], event.geometry['x1'],event.geometry['y0'],event.geometry['y1']
            callback(xmin, xmax, ymin, ymax)
        
        self.chart.on_event(events.SelectionGeometry, temp_callback)


class Line(BaseLine):
    """
        Description:
    """
    reset_event = events.Reset
    data_y_axis = 'y'
    data_x_axis = 'x'
    use_data_tiles = False

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

    def format_source_data(self, data):
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
        self.source = data
        self.x_range = (self.source[self.x].min(), self.source[self.x].max())
        self.y_range = (self.source[self.y].min(), self.source[self.y].max())

    def generate_InteractiveImage_callback(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def viewInteractiveImage(x_range, y_range, w, h, data_source):
            cvs = cds.Canvas(plot_width=w, plot_height=h, x_range=x_range, y_range=y_range)
            agg = cvs.line(source=data_source, x=self.x, y=self.y)
            img= tf.shade(agg, cmap=['white', self.color], how=self.pixel_shade_type)
            return img
    
        return viewInteractiveImage
            
    def generate_chart(self):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.color == '#8735fb':
            self.color = 'rapidspurple'
        
        elif re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', self.color):
            print('enter color name instead of hex')
            self.color = 'rapidspurple'

        self.chart = figure(title="Line plot for "+self.aggregate_fn, toolbar_location="right", tools="pan, wheel_zoom, reset", active_scroll='wheel_zoom', active_drag='pan',
                            x_range=self.x_range, y_range = self.y_range, width=self.width, height=self.height)

        self.chart.add_tools(BoxSelectTool())
        # self.chart.add_tile(self.tile_provider)
        # self.chart.axis.visible = False

        self.chart.xgrid.grid_line_color = None
        self.chart.ygrid.grid_line_color = None

        self.interactive_image = InteractiveImage(self.chart, self.generate_InteractiveImage_callback(), data_source=self.source)
        
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

    def reload_chart(self, data, update_source=False):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if data is not None:        
            self.interactive_image.update_chart(data_source=data)
            if update_source:
                self.format_source_data(data)

    def reset_chart_geometry_ranges(self):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        # self.chart.x_range.start,self.chart.x_range.end = self.chart.x_range.reset_start,self.chart.x_range.reset_end
        # self.chart.y_range.start,self.chart.y_range.end = self.chart.y_range.reset_start,self.chart.y_range.reset_end
        # self.get_selection_geometry_callback()(self.chart.x_range.start,self.chart.x_range.end, self.chart.y_range.start,self.chart.y_range.end)
        # self.source = self.interactive_image.kwargs['data_source']

    def add_selection_geometry_event(self, callback):
        '''
        Description:
        
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        def temp_callback(event):
            xmin, xmax, ymin, ymax = event.geometry['x0'], event.geometry['x1'],event.geometry['y0'],event.geometry['y1']
            callback(xmin, xmax, ymin, ymax)
        
        self.chart.on_event(events.SelectionGeometry, temp_callback)
