from typing import Dict

class BaseWidget:
    chart_type: str = None
    x: str = None
    color: str = None
    height: int = None
    width: int = None
    chart = None
    data_points: int = 100
    start: float  = None
    end: float = None
    _stride = None
    stride_type = int
    params = None
    min_value: float = 0.0
    max_value: float = 0.0
    label_map: Dict[str, str] = None
    use_data_tiles = False

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
            # elif self.data_points != int((self.max_value - self.min_value)/value):
            #     self.data_points = int((self.max_value - self.min_value)/value)
                
            self._stride = value
        
    def __init__(self, x, width=400, height=10, data_points=100, step_size=None, step_size_type=int, **params):
        '''
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.x = x
        self.width = width
        self.height = height
        self.params = params
        self.data_points = data_points
        self.stride = step_size
        self.stride_type = step_size_type
        if 'value' in params:
            self.value = params['value']
            params.pop('value')
        if 'label_map' in params:
            self.label_map = params['label_map']
            self.label_map = {v: k for k, v in self.label_map.items()}
            params.pop('label_map')
    
    def view(self):
        return self.chart

    def add_event(self, event, callback):
        self.chart.on_event(event, callback)

    def compute_query_dict(self, query_dict):
        print('base calc source function, to over-ridden by delegated classes')
    
    def reload_chart(self, *args, **kwargs):
        #No reload functionality, added function for consistency with other charts
        return -1
    
    # def add_int_slider_filter(self, min_value, max_value, data_points, value=None, **kwargs):
    #     '''
    #     add range slider to the bottom of the chart, for the filter function
    #      to facilitate interaction behavior, that updates the rest of the charts on the page, using datatiles
    #     '''
    #     self.filter_widget = int_slider(min_value, max_value, data_points, value=value, **kwargs)

    # def add_float_slider_filter(self, min_value, max_value, data_points, value=None, **kwargs):
    #     '''
    #     add range slider to the bottom of the chart, for the filter function
    #      to facilitate interaction behavior, that updates the rest of the charts on the page, using datatiles
    #     '''
    #     self.filter_widget = float_slider(min_value, max_value, data_points, value=value, **kwargs)
