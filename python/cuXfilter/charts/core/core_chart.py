import numpy as np
from typing import Dict


class BaseChart:
    chart_type: str = None
    x: str = None
    y: str = None
    aggregate_fn: str = 'count'
    color: str = None
    _height: int = 0
    _width: int = 0
    add_interaction: bool = True
    chart = None
    source = None
    source_backup = None
    data_points: int = 0
    filter_widget = None
    _library_specific_params: Dict[str, str] = {}
    _stride = None
    stride_type = int
    min_value: float = 0.0
    max_value: float = 0.0
    x_label_map = {}
    y_label_map = {}

    @property
    def name(self):
        return self.x+"_"+self.chart_type

    @property
    def stride(self):
        return self._stride

    @stride.setter
    def stride(self, value):
        if value is None:
            self._stride = None
        else:
            # value = round(value, 2)
            if self.stride_type == int:
                value = self.stride_type(value)
            
            if self.stride_type(value) == self.stride_type(0):
                value = self.stride_type(1.0)
            
            if self.data_points != int((self.max_value - self.min_value)/value):
                self.data_points = int((self.max_value - self.min_value)/value)
                
            self._stride = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        if self.chart is not None:
            self.update_dimensions(width=value)
        if self.filter_widget is not None:
            self.filter_widget.width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if self.chart is not None:
            self.update_dimensions(height=value)

    @property
    def library_specific_params(self):
        return self._library_specific_params

    @library_specific_params.setter
    def library_specific_params(self, value):
        self._library_specific_params = value
        self.extract_mappers()
        self.set_color()

    def set_color(self):
        self.color = '#8735fb'
        if 'color' in self.library_specific_params:
            self.color = self.library_specific_params['color']

    def extract_mappers(self):
        if 'x_label_map' in self.library_specific_params:
            self.x_label_map = self.library_specific_params['x_label_map']
            self.library_specific_params.pop('x_label_map')
        if 'y_label_map' in self.library_specific_params:
            self.y_label_map = self.library_specific_params['y_label_map']
            self.library_specific_params.pop('y_label_map')

    def view(self):
        return self.chart

    def update_dimensions(self, width=None, height=None):
        print('base calc source function, to over-ridden by delegated classes')

    def calculate_source(self, data):
        print('base calc source function, to over-ridden by delegated classes')
    
    def generate_chart(self):
        print('base calc source function, to over-ridden by delegated classes')

    def add_reset_event(self, callback=None):
        print('base calc source function, to over-ridden by delegated classes')

    def add_event(self, event, callback):
        self.chart.on_event(event, callback)

    def compute_query_dict(self, query_dict):
        print('base calc source function, to over-ridden by delegated classes')

    def reset_chart(self, data:list=[]):
        print('base calc source function, to over-ridden by delegated classes')

    def reload_chart(self, data, patch_update:bool):
        print('base calc source function, to over-ridden by delegated classes')

    def format_source_data(self, source_dict, patch_update= False):
        '''
        '''
        # print('function to be overridden by library specific extensions')

    def get_source_y_axis(self):
        # print('function to be overridden by library specific extensions')
        return []

    def apply_mappers(self):
        '''
        '''
        # print('function to be overridden by library specific extensions')

    