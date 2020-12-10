import os
from . import plots
from ..constants import CUXF_NAN_COLOR


def choropleth(
    x,
    color_column,
    elevation_column=None,
    color_aggregate_fn="count",
    color_factor=1,
    elevation_aggregate_fn="sum",
    elevation_factor=1,
    add_interaction=True,
    width=800,
    height=400,
    geoJSONSource=None,
    geoJSONProperty=None,
    geo_color_palette=None,
    mapbox_api_key=os.getenv("MAPBOX_API_KEY"),
    map_style=None,
    tooltip=True,
    tooltip_include_cols=[],
    nan_color=CUXF_NAN_COLOR,
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

    elevation_column: str  | Optional
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
        factor to be multiplied to each value of elevation column before
        scaling the elevation

    add_interaction: {True, False},  default True

    width: int,  default 800

    height: int,  default 400

    geoJSONSource: str
        url to the geoJSON file

    geoJSONProperty: str,  optional
        Property to use while doing aggregation operations using
        the geoJSON file.
        Defaults to the first value in properties in geoJSON file.

    geo_color_palette: bokeh.palette,  default bokeh.palettes.Inferno256

    mapbox_api_key: str, default os.getenv('MAPBOX_API_KEY')

    map_style: str,
        default based on cuxfilter.themes:
            dark/rapids theme: 'mapbox://styles/mapbox/dark-v9'
            light theme: 'mapbox://styles/mapbox/light-v9'
        URI for Mapbox basemap style.
        See Mapbox's `https://docs.mapbox.com/mapbox-gl-js/example/setstyle/`
        for examples

    tooltip: {True, False},  default True

    tooltip_include_cols: [], default list(dataframe.columns)

    nan_color: hex color code, default cuxfilter.charts.CUXF_NAN_COLOR
        color of the patches of value NaN in the map.


    title: str,

        chart title

    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type 3dchoropleth
    """
    plot = plots.Choropleth(
        x,
        color_column,
        elevation_column,
        color_aggregate_fn,
        color_factor,
        elevation_aggregate_fn,
        elevation_factor,
        add_interaction,
        width,
        height,
        geoJSONSource,
        geoJSONProperty,
        geo_color_palette,
        mapbox_api_key,
        map_style,
        tooltip,
        tooltip_include_cols,
        nan_color,
        **library_specific_params,
    )
    plot.chart_type = "choropleth"
    return plot
