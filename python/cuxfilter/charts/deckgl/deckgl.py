from . import plots
import os


def choropleth3d(
    x,
    color_column,
    elevation_column,
    color_aggregate_fn="count",
    color_factor=1,
    elevation_aggregate_fn="sum",
    elevation_factor=1,
    data_points=100,
    add_interaction=True,
    width=800,
    height=400,
    step_size=None,
    step_size_type=int,
    geoJSONSource=None,
    geoJSONProperty=None,
    geo_color_palette=None,
    mapbox_api_key=os.getenv('MAPBOX_API_KEY'),
    map_style='dark',
    **library_specific_params,
):
    """

    Parameters
    ----------
    x: str
        x-axis column name from the gpu dataframe

    color_column: str
        column name from the gpu dataframe on which color palettes
        are based on

    elevation_column: str
        column name from the gpu dataframe on which elevation scale
        is based on

    color_aggregate_fn: {'count', 'mean', 'sum', 'min', 'max', 'std'},
    default "count"
        aggregate function to be applied on the color column
        while performing groupby aggregation by `column x`

    color_factor: float, default 1
        factor to be multiplied to each value of color column before mapping
        the color

    elevation_aggregate_fn: {'count', 'mean', 'sum', 'min', 'max', 'std'},
    default "count"
        aggregate function to be applied on the elevation column
        while performing groupby aggregation by `column x`

    elevation_factor: float, default 1
        factor to be multiplied to each value of elevation column before scaling
        the elevation

    data_points: int,  default 100

    add_interaction: {True, False},  default True

    width: int,  default 800

    height: int,  default 400

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    # x_label_map: dict,  default None
    #     label maps for x axis
    #     {value: mapped_str}
    # y_label_map: dict,  default None
    #     label maps for y axis
    #     {value: mapped_str}

    geoJSONSource: str
        url to the geoJSON file

    geoJSONProperty: str,  optional
        Property to use while doing aggregation operations using
        the geoJSON file.
        Defaults to the first value in properties in geoJSON file.

    geo_color_palette: bokeh.palette,  default bokeh.palettes.Inferno256

    nan_color: str, default white
        color of the patches of value NaN in the map.

    mapbox_api_key: str, default os.getenv('MAPBOX_API_KEY')

    map_style: {'dark', 'light'}, default 'dark'
        map background type
    tooltip: {True, False},  default True
    
    title: str,

        chart title

    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type 3dchoropleth
    """
    return plots.Choropleth3d(
        x,
        color_column,
        elevation_column,
        color_aggregate_fn,
        color_factor,
        elevation_aggregate_fn,
        elevation_factor,
        data_points,
        add_interaction,
        width,
        height,
        step_size,
        step_size_type,
        geoJSONSource,
        geoJSONProperty,
        geo_color_palette,
        mapbox_api_key,
        map_style,
        **library_specific_params,
    )
