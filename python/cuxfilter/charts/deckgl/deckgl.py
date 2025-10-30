# SPDX-FileCopyrightText: Copyright (c) 2020-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

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
    geoJSONSource=None,
    geoJSONProperty=None,
    geo_color_palette=None,
    mapbox_api_key=os.getenv("MAPBOX_API_KEY"),
    map_style=None,
    tooltip=True,
    tooltip_include_cols=[],
    nan_color=CUXF_NAN_COLOR,
    title="",
    x_range=None,
    y_range=None,
    opacity=None,
    layer_spec={},  # deck.gl layer spec
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
            dark/rapids_dark theme: 'mapbox://styles/mapbox/dark-v9'
            default/rapids theme: 'mapbox://styles/mapbox/light-v9'
        URI for Mapbox basemap style.
        See Mapbox's `https://docs.mapbox.com/mapbox-gl-js/example/setstyle/`
        for examples

    tooltip: {True, False},  default True

    tooltip_include_cols: [], default list(dataframe.columns)

    nan_color: hex color code, default cuxfilter.charts.CUXF_NAN_COLOR
        color of the patches of value NaN in the map.


    title: str,
        chart title

    x_range: tuple, default None (it's calculated automatically)
        tuple of min and max values for x-axis

    y_range: tuple, default None (it's calculated automatically)
        tuple of min and max values for y-axis

    opacity: float, default None
        opacity of the chart

    layer_spec: dict, default {}
        deck.gl layer spec dictionary to override the default layer spec. For
        more information,
        see https://deck.gl/docs/api-reference/layers/polygon-layer

    Returns
    -------
    A bokeh chart object of type choropleth (2d or 3d depending on the value
        of elevation_column)
    """
    plot = plots.Choropleth(
        x=x,
        color_column=color_column,
        elevation_column=elevation_column,
        color_aggregate_fn=color_aggregate_fn,
        color_factor=color_factor,
        elevation_aggregate_fn=elevation_aggregate_fn,
        elevation_factor=elevation_factor,
        add_interaction=add_interaction,
        geoJSONSource=geoJSONSource,
        geoJSONProperty=geoJSONProperty,
        geo_color_palette=geo_color_palette,
        mapbox_api_key=mapbox_api_key,
        map_style=map_style,
        tooltip=tooltip,
        tooltip_include_cols=tooltip_include_cols,
        nan_color=nan_color,
        title=title,
        x_range=x_range,
        y_range=y_range,
        opacity=opacity,
        layer_spec=layer_spec,
    )
    plot.chart_type = "choropleth"
    return plot
