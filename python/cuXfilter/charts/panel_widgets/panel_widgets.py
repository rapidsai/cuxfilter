from .plots import RangeSlider, IntSlider, FloatSlider, DropDown, MultiSelect, DataSizeIndicator

def range_slider(x, width=400, height=10, data_points=100, step_size=None, step_size_type=int,  **params):
    return RangeSlider(x, width, height, data_points,step_size, step_size_type,  **params)

def int_slider(x, width=400, height=10, data_points=100, step_size=None, step_size_type=int,  **params):
    return IntSlider(x, width, height, data_points,step_size, step_size_type,  **params)

def float_slider(x, width=400, height=10, data_points=100, step_size=None, step_size_type=int,  **params):
    return FloatSlider(x, width, height, data_points, step_size, step_size_type, **params)

def drop_down(x, width=400, height=20,  **params):
    return DropDown(x, width, height,  **params)

def multi_select(x, width=400, height=200, **params):
    return MultiSelect(x, width, height, **params)

def data_size_indicator(width=400, height=50, **library_specific_params):
    return DataSizeIndicator(width, height, **library_specific_params)
