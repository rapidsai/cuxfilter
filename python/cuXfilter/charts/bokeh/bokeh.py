from . import plots


def bar(
    x, y=None, data_points=100, add_interaction=True, aggregate_fn='count',
    width=400, height=400, step_size=None, step_size_type=int,
    **library_specific_params
):
    """
    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    data_points: int,  default 100

    add_interaction: {True, False},  default True

    aggregate_fn: {'count', 'mean'},  default 'count'

    width: int,  default 400

    height: int,  default 400

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    x_label_map: dict,  default None
        label maps for x axis
        {value: mapped_str}
    y_label_map: dict,  default None
        label maps for y axis
        {value: mapped_str}

    title: str,

        chart title

    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type vbar
    """
    return plots.Bar(
        x, y, data_points, add_interaction, aggregate_fn, width,
        height, step_size, step_size_type,
        **library_specific_params
    )


def line(
    x, y=None, data_points=100, add_interaction=True, aggregate_fn='count',
    width=400, height=400, step_size=None, step_size_type=int,
    **library_specific_params
):
    """

    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    data_points: int,  default 100

    add_interaction: {True, False},  default True

    aggregate_fn: {'count', 'mean'},  default 'count'

    width: int,  default 400

    height: int,  default 400

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    x_label_map: dict,  default None
        label maps for x axis
        {value: mapped_str}
    y_label_map: dict,  default None
        label maps for y axis
        {value: mapped_str}

    title: str,

        chart title
    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type line
    """
    return plots.Line(
        x, y, data_points, add_interaction, aggregate_fn, width, height,
        step_size, step_size_type, **library_specific_params
    )


def choropleth(
    x, y=None, data_points=100, add_interaction=True, aggregate_fn='count',
    width=800, height=400, step_size=None, step_size_type=int,
    geoJSONSource=None, geoJSONProperty=None, geo_color_palette=None,
    tile_provider=None, **library_specific_params
):
    """

    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    data_points: int,  default 100

    add_interaction: {True, False},  default True

    aggregate_fn: {'count', 'mean'},  default 'count'
        defaults to 'count'
    width: int,  default 800

    height: int,  default 400

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    x_label_map: dict,  default None
        label maps for x axis
        {value: mapped_str}
    y_label_map: dict,  default None
        label maps for y axis
        {value: mapped_str}
    geoJSONSource: str
        url to the geoJSON file
    geoJSONProperty: str,  optional
        Property to use while doing aggregation operations using
        the geoJSON file.
        Defaults to the first value in properties in geoJSON file.
    geo_color_palette: bokeh.palette,  default bokeh.palettes.Inferno256

    nan_color: str, default white
        color of the patches of value NaN in the map.

    tile_provider: bokeh.tile_provider object or
            cuXfilter.assets.custom_tiles.get_provider object, default None

    title: str,

        chart title

    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type choropleth
    """
    return plots.Choropleth(
        x, y, data_points, add_interaction, aggregate_fn, width, height,
        step_size, step_size_type, geoJSONSource, geoJSONProperty,
        geo_color_palette, tile_provider, **library_specific_params
    )
