from . import plots

def scatter_geo(x, y=None, x_range=None, y_range=None, add_interaction=True, color_palette=None, aggregate_col=None, aggregate_fn='count', point_size=1, point_shape='circle', pixel_shade_type='eq_hist', pixel_density=0.5, pixel_spread='dynspread', width=800, height=400, tile_provider='CARTODBPOSITRON', **library_specific_params):
    """
    
    Parameters
    ----------

    x: str 
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    x_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
    y_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
            
    add_interaction: {True, False},  default True
         
    color_palette: bokeh.palettes or list of hex_color_codes, or list of color names,  default inferno

    aggregate_col: str, default None
        Column from the gpu dataframe on which the aggregate_fn will be run on, if None, aggregate_fn is run on y-column.

    aggregate_fn: {'count', 'mean', 'max', 'min'},  default 'count'

    point_size: int, default 1
        Point size in the scatter plot.

    point_shape: str, default 'circle'
        Available options: circle, square, rect_vertical, rect_horizontal.

    pixel_shade_type: str, default 'eq_hist'
        The "how" parameter in cudatashader.transfer_functions.shade() function.
        Available options: eq_hist, linear, log, cbrt

    pixel_density: float, default 0.5
        A tuning parameter in [0, 1], with higher values giving more dense scatter plot.

    pixel_spread: str, default 'dynspread'
        dynspread: Spread pixels in an image dynamically based on the image density.
        spread: Spread pixels in an image.
    
    width: int,  default 800
        
    height: int,  default 400
        
    tile_provider: str, default 'CARTODBPOSITRON'
        Underlying map type. See https://bokeh.pydata.org/en/latest/docs/reference/tile_providers.html
    **library_specific_params:
        additional library specific keyword arguments to be passed to the function

    Returns
    -------
    A cudashader geo-scatter plot. Type cuXfilter.charts.cudatashader.custom_extensions.InteractiveImage
    """
    return plots.ScatterGeo(x, y, x_range, y_range, add_interaction, color_palette, aggregate_col, aggregate_fn, point_size, point_shape, pixel_shade_type, pixel_density, pixel_spread, width, height, tile_provider, **library_specific_params)

def scatter(x, y, x_range=None, y_range=None, add_interaction=True, color_palette=None, aggregate_col=None, aggregate_fn='count', point_size=1, point_shape='circle', pixel_shade_type='eq_hist', pixel_density=0.5, pixel_spread='dynspread', width=800, height=400, **library_specific_params):
    """
    
    Parameters
    ----------

    x: str 
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    x_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
    y_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
            
    add_interaction: {True, False},  default True
    
    color_palette: bokeh.palettes or list of hex_color_codes, or list of color names,  default inferno

    aggregate_col: str, default None
        column from the gpu dataframe on which the aggregate_fn will be run on, if None, aggregate_fn is run on y-column

    aggregate_fn: {'count', 'mean', 'max', 'min'},  default 'count'

    point_size: int, default 1
        Point size in the scatter plot.

    point_shape: str, default 'circle'
        Available options: circle, square, rect_vertical, rect_horizontal.

    pixel_shade_type: str, default 'eq_hist'
        The "how" parameter in cudatashader.transfer_functions.shade() function.
        Available options: eq_hist, linear, log, cbrt

    pixel_density: float, default 0.5
        A tuning parameter in [0, 1], with higher values giving more dense scatter plot.

    pixel_spread: str, default 'dynspread'
        dynspread: Spread pixels in an image dynamically based on the image density.
        spread: Spread pixels in an image.

    width: int,  default 800
        
    height: int,  default 400
        
    **library_specific_params:
        additional library specific keyword arguments to be passed to the function

    Returns
    -------
    A cudashader scatter plot. Type cuXfilter.charts.cudatashader.custom_extensions.InteractiveImage
    """
    return plots.Scatter(x, y, x_range, y_range, add_interaction, color_palette, aggregate_col, aggregate_fn, point_size, point_shape, pixel_shade_type, pixel_density, pixel_spread,  width, height, **library_specific_params)


def heatmap(x, y, x_range=None, y_range=None, add_interaction=True, color_palette=None, aggregate_col=None, aggregate_fn='mean', point_size=10, point_shape='rect_vertical', width=800, height=400, **library_specific_params):
    """
    Heatmap using default cudatashader.scatter plot with slight modifications. 
    Added for better defaults. In theory, scatter directly can be used to generate the same.

    Parameters
    ----------

    x: str 
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    x_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
    y_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
            
    add_interaction: {True, False},  default True
    
    color_palette: bokeh.palettes or list of hex_color_codes, or list of color names,  default inferno

    aggregate_col: str, default None
        column from the gpu dataframe on which the aggregate_fn will be run on, if None, aggregate_fn is run on y-column

    aggregate_fn: {'count', 'mean', 'max', 'min'},  default 'count'

    point_size: int, default 1
        Point size in the scatter plot.

    point_shape: str, default 'rect_vertical'
        Available options: circle, square, rect_vertical, rect_horizontal.

    pixel_density: float, default 0.5
        A tuning parameter in [0, 1], with higher values giving more dense scatter plot.

    pixel_spread: str, default 'dynspread'
        dynspread: Spread pixels in an image dynamically based on the image density.
        spread: Spread pixels in an image.

    width: int,  default 800
        
    height: int,  default 400
        
    **library_specific_params:
        additional library specific keyword arguments to be passed to the function

    Returns
    -------
    A cudashader heatmap (scatter object). Type cuXfilter.charts.cudatashader.custom_extensions.InteractiveImage
    """
    return plots.Scatter(x, y, x_range, y_range, add_interaction, color_palette, aggregate_col, aggregate_fn, point_size, point_shape, 'linear', 1, 'spread',  width, height, **library_specific_params)

def line(x, y=None, data_points=100, add_interaction=True, aggregate_fn='count', pixel_shade_type='linear', width=400, height=400,step_size=None, step_size_type=int, **library_specific_params):
    """
    
    Parameters
    ----------

    x: str 
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    x_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
    y_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].min())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
            
    add_interaction: {True, False},  default True

    aggregate_col: str, default None
        column from the gpu dataframe on which the aggregate_fn will be run on, if None, aggregate_fn is run on y-column

    aggregate_fn: {'count', 'mean', 'max', 'min'},  default 'count'

    pixel_shade_type: str, default 'linear'
        The "how" parameter in cudatashader.transfer_functions.shade() function.
        Available options: eq_hist, linear, log, cbrt

    width: int,  default 800
        
    height: int,  default 400
        
    **library_specific_params:
        additional library specific keyword arguments to be passed to the function

    Returns
    -------
    A cudashader scatter plot. Type cuXfilter.charts.cudatashader.custom_extensions.InteractiveImage
    """
    return plots.Line(x, y, data_points, add_interaction, aggregate_fn, pixel_shade_type, width, height,  step_size, step_size_type, **library_specific_params)