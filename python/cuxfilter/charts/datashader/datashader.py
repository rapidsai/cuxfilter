from . import plots


def scatter(
    x,
    y,
    x_range=None,
    y_range=None,
    add_interaction=True,
    color_palette=None,
    aggregate_col=None,
    aggregate_fn="count",
    point_size=15,
    point_shape="circle",
    pixel_shade_type="eq_hist",
    pixel_density=0.5,
    pixel_spread="dynspread",
    tile_provider=None,
    width=800,
    height=400,
    title="",
    timeout=100,
    legend=True,
    legend_position="top_right",
    unselected_alpha=0.2,
    **library_specific_params,
):
    """
    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    x_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
    y_range: tuple, default(gpu_dataframe[y].min(), gpu_dataframe[y].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed

    add_interaction: {True, False},  default True

    color_palette: bokeh.palettes or list/tuple of hex_color_codes,
        or list/tuple of color names, default bokeh.palettes.Virisdis10

    aggregate_col: str, default None
        column from the gpu dataframe on which the aggregate_fn will be run on,
        if None, aggregate_fn is run on y-column

    aggregate_fn: {'count', 'mean', 'max', 'min'},  default 'count'

    point_size: int, default 1
        Point size in the scatter plot.

    point_shape: str, default 'circle'
        Available options: circle, square, rect_vertical, rect_horizontal.

    pixel_shade_type: str, default 'eq_hist'
        The "how" parameter in datashader.transfer_functions.shade()
        function.
        Available options: eq_hist, linear, log, cbrt

    pixel_density: float, default 0.5
        A tuning parameter in [0, 1], with higher values giving more dense
        scatter plot.

    pixel_spread: str, default 'dynspread'
        dynspread: Spread pixels in an image dynamically based on the image
        density.
        spread: Spread pixels in an image.

    tile_provider: str, default None
        Underlying map type.See
        https://holoviews.org/reference/elements/bokeh/Tiles.html

    width: int,  default 800

    height: int,  default 400

    title: str,

        chart title

    timeout: int (milliseconds), default 100
        Determines the timeout after which the callback will
        process new events without the previous one having
        reported completion. Increase for very long running
        callbacks and if zooming feels laggy.

    legend: bool, default True
        Adds Bokeh.models.LinearColorMapper based legend if True,
        Note: legend currently only works with pixel_shade_type='linear'/'log'

    legend_position: str, default top_right
        position of legend on the chart.
        Valid places are: right, left, bottom, top, top_right, top_left,
                        bottom_left, bottom_right

    unselected_alpha: float [0, 1], default 0.2
        if True, displays unselected data in the same color_palette
        but transparent(alpha=0.2)

    **library_specific_params:
        additional library specific keyword arguments to be passed to the
        function

    Returns
    -------
    A cudashader scatter plot of type:
        cuxfilter.charts.datashader.custom_extensions.InteractiveDatashaderPoints
    """
    plot = plots.Scatter(
        x,
        y,
        x_range,
        y_range,
        add_interaction,
        color_palette,
        aggregate_col,
        aggregate_fn,
        point_size,
        point_shape,
        pixel_shade_type,
        pixel_density,
        pixel_spread,
        width,
        height,
        tile_provider=tile_provider,
        title=title,
        timeout=timeout,
        legend=legend,
        legend_position=legend_position,
        unselected_alpha=unselected_alpha,
        **library_specific_params,
    )

    plot.chart_type = "scatter"
    return plot


def graph(
    node_x="x",
    node_y="y",
    node_id="vertex",
    edge_source="source",
    edge_target="target",
    x_range=None,
    y_range=None,
    add_interaction=True,
    node_aggregate_col=None,
    edge_aggregate_col=None,
    node_aggregate_fn="count",
    edge_aggregate_fn="count",
    node_color_palette=None,
    edge_color_palette=["#000000"],
    node_point_size=15,
    node_point_shape="circle",
    node_pixel_shade_type="eq_hist",
    node_pixel_density=0.8,
    node_pixel_spread="dynspread",
    edge_render_type="direct",
    edge_transparency=0,
    curve_params=dict(strokeWidth=1, curve_total_steps=100),
    tile_provider=None,
    width=800,
    height=400,
    title="",
    timeout=100,
    legend=True,
    legend_position="top_right",
    unselected_alpha=0.2,
    **library_specific_params,
):

    """
    Parameters
    ----------
    node_x: str, default "x"
        x-coordinate column name for the nodes cuDF dataframe

    node_y: str, default "y"
        y-coordinate column name for the nodes cuDF dataframe

    node_id: str, default "vertex"
        node_id/label column name for the nodes cuDF dataframe

    edge_source: str, default "source"
        edge_source column name for the edges cuDF dataframe

    edge_target="target",
        edge_target column name for the edges cuDF dataframe

    x_range: tuple, default(nodes_gpu_dataframe[x].min(),
        nodes_gpu_dataframe[x].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed

    y_range: tuple, default(nodes_gpu_dataframe[y].min(),
    nodes_gpu_dataframe[y].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed

    add_interaction: {True, False},  default True

    node_aggregate_col=str, default None,
        column from the nodes gpu dataframe on which the mode_aggregate_fn
        will be run on

    edge_aggregate_col=str, default None,
        column from the edges gpu dataframe on which the mode_aggregate_fn
        will be run on

    node_aggregate_fn={'count', 'mean', 'max', 'min'},  default 'count'
    edge_aggregate_fn={'count', 'mean', 'max', 'min'},  default 'count'

    node_color_palette=bokeh.palettes or list/tuple of hex_color_codes,
        or list/tuple of color names, default bokeh.palettes.Virisdis10

    edge_color_palette=bokeh.palettes or list/tuple of hex_color_codes,
        or list/tuple of color names, default ["#000000"]

    node_point_size: int, default 8
        Point size in the scatter plot.

    node_point_shape: str, default 'circle'
        Available options: circle, square, rect_vertical, rect_horizontal.

    node_pixel_shade_type: str, default 'eq_hist'
        The "how" parameter in datashader.transfer_functions.shade()
        function.
        Available options: eq_hist, linear, log, cbrt

    node_pixel_density: float, default 0.8
        A tuning parameter in [0, 1], with higher values giving more dense
        scatter plot.

    node_pixel_spread: str, default 'dynspread'
        dynspread: Spread pixels in an image dynamically based on the image
        density.
        spread: Spread pixels in an image.

    edge_render_type: str, default 'direct'
        type of edge render. Available options are 'direct'/'curved'
        *Note: Curved edge rendering is an experimental feature and may throw
        out of memory errors

    edge_transparency: float, default 0
        value in range [0,1] to specify transparency level of edges, with
        1 being completely transparent

    curve_params: dict, default dict(strokeWidth=1, curve_total_steps=100)
        control curvature and max_bundle_size if edge_render_type='curved'

    tile_provider: str, default None
        Underlying map type.See
        https://holoviews.org/reference/elements/bokeh/Tiles.html

    width: int,  default 800

    height: int,  default 400

    title: str,

        chart title

    timeout: int (milliseconds), default 100
        Determines the timeout after which the callback will
        process new events without the previous one having
        reported completion. Increase for very long running
        callbacks and if zooming feels laggy.

    legend: bool, default True
        Adds Bokeh.models.LinearColorMapper based legend if True,
        Note: legend currently only works with pixel_shade_type='linear'/'log'

    legend_position: str, default top_right
        position of legend on the chart.
        Valid places are: right, left, bottom, top, top_right, top_left,
                        bottom_left, bottom_right

    unselected_alpha: float [0, 1], default 0.2
        if True, displays unselected data in the same color_palette
        but transparent(alpha=0.2) (nodes only)

    **library_specific_params:
        additional library specific keyword arguments to be passed to the
        function

    Returns
    -------
    A cudashader graph plot of type:
        cuxfilter.charts.datashader.custom_extensions.InteractiveDatashaderGraph
    """
    plot = plots.Graph(
        node_x,
        node_y,
        node_id,
        edge_source,
        edge_target,
        x_range,
        y_range,
        add_interaction,
        node_aggregate_col,
        edge_aggregate_col,
        node_aggregate_fn,
        edge_aggregate_fn,
        node_color_palette,
        edge_color_palette,
        node_point_size,
        node_point_shape,
        node_pixel_shade_type,
        node_pixel_density,
        node_pixel_spread,
        edge_render_type,
        edge_transparency,
        curve_params,
        tile_provider,
        width,
        height,
        title,
        timeout,
        legend=legend,
        legend_position=legend_position,
        unselected_alpha=unselected_alpha,
        **library_specific_params,
    )

    plot.chart_type = "graph"
    return plot


def heatmap(
    x,
    y,
    x_range=None,
    y_range=None,
    add_interaction=True,
    color_palette=None,
    aggregate_col=None,
    aggregate_fn="mean",
    point_size=15,
    point_shape="rect_vertical",
    width=800,
    height=400,
    title="",
    timeout=100,
    legend=True,
    legend_position="top_right",
    unselected_alpha=0.2,
    **library_specific_params,
):
    """
    Heatmap using default datashader.scatter plot with slight modifications.
    Added for better defaults. In theory, scatter directly can be used
    to generate the same.

    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    x_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
    y_range: tuple, default(gpu_dataframe[y].min(), gpu_dataframe[y].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed

    add_interaction: {True, False},  default True

    color_palette: bokeh.palettes or list/tuple of hex_color_codes,
        or list/tuple of color names, default bokeh.palettes.Virisdis10

    aggregate_col: str, default None
        column from the gpu dataframe on which the aggregate_fn will be run on,
        if None, aggregate_fn is run on y-column

    aggregate_fn: {'count', 'mean', 'max', 'min'},  default 'count'

    point_size: int, default 1
        Point size in the scatter plot.

    point_shape: str, default 'rect_vertical'
        Available options: circle, square, rect_vertical, rect_horizontal.

    pixel_density: float, default 0.5
        A tuning parameter in [0, 1], with higher values giving more dense
        scatter plot.

    pixel_spread: str, default 'dynspread'
        dynspread: Spread pixels in an image dynamically based on the image
        density.
        spread: Spread pixels in an image.

    width: int,  default 800

    height: int,  default 400

    title: str,

        chart title

    timeout: int (milliseconds), default 100
        Determines the timeout after which the callback will
        process new events without the previous one having
        reported completion. Increase for very long running
        callbacks and if zooming feels laggy.

    legend: bool, default True
        Adds Bokeh.models.LinearColorMapper based legend if True,

    legend_position: str, default top_right
        position of legend on the chart.
        Valid places are: right, left, bottom, top, top_right, top_left,
                        bottom_left, bottom_right

    unselected_alpha: float [0, 1], default 0.2
        if True, displays unselected data in the same color_palette
        but transparent(alpha=0.2)

    **library_specific_params:
        additional library specific keyword arguments to be passed to the
        function

    Returns
    -------
    A cudashader heatmap (scatter object) of type:
        cuxfilter.charts.datashader.custom_extensions.InteractiveDatashaderPoints
    """
    plot = plots.Scatter(
        x,
        y,
        x_range,
        y_range,
        add_interaction,
        color_palette,
        aggregate_col,
        aggregate_fn,
        point_size,
        point_shape,
        "linear",
        1,
        "spread",
        width,
        height,
        tile_provider=None,
        title=title,
        timeout=timeout,
        legend=legend,
        legend_position=legend_position,
        unselected_alpha=unselected_alpha,
        **library_specific_params,
    )
    plot.chart_type = "heatmap"
    return plot


def line(
    x,
    y,
    data_points=100,
    add_interaction=True,
    pixel_shade_type="linear",
    color=None,
    step_size=None,
    step_size_type=int,
    width=800,
    height=400,
    title="",
    timeout=100,
    unselected_alpha=0.2,
    **library_specific_params,
):
    """

    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str
        y-axis column name from the gpu dataframe
    x_range: tuple, default(gpu_dataframe[x].min(), gpu_dataframe[x].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed
    y_range: tuple, default(gpu_dataframe[y].min(), gpu_dataframe[y].max())
        (min, max) x-dimensions of the geo-scatter plot to be displayed

    add_interaction: {True, False},  default True

    pixel_shade_type: str, default 'linear'
        The "how" parameter in datashader.transfer_functions.shade()
        function.
        Available options: eq_hist, linear, log, cbrt

    color: str,  default #8735fb

    step_size: int, default None
        for the range_slider below the chart

    step_size_type: type, default int
        for the range_slider below the chart

    width: int,  default 800

    height: int,  default 400

    title: str,

        chart title

    timeout: int (milliseconds), default 100
        Determines the timeout after which the callback will
        process new events without the previous one having
        reported completion. Increase for very long running
        callbacks and if zooming feels laggy.

    unselected_alpha: float [0, 1], default 0.2
        if True, displays unselected data in the same color_palette
        but transparent(alpha=0.2)

    **library_specific_params:
        additional library specific keyword arguments to be passed to the
        function

    Returns
    -------
    A cudashader scatter plot of type:
        cuxfilter.charts.datashader.custom_extensions.InteractiveDatashaderLine
    """
    plot = plots.Line(
        x,
        y,
        data_points,
        add_interaction,
        pixel_shade_type,
        color,
        step_size,
        step_size_type,
        width,
        height,
        title,
        timeout,
        unselected_alpha=unselected_alpha,
        **library_specific_params,
    )
    plot.chart_type = "non_aggregate_line"
    return plot


def stacked_lines(
    x,
    y,
    data_points=100,
    add_interaction=True,
    colors=[],
    step_size=None,
    step_size_type=int,
    width=800,
    height=400,
    title="",
    timeout=100,
    legend=True,
    legend_position="top_right",
    unselected_alpha=0.2,
    **library_specific_params,
):
    """
    stacked lines chart

    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: list
        y-axis column names from the gpu dataframe for the stacked lines

    add_interaction: {True, False},  default True

    colors: list, default [#8735fb, #8735fb, ....]

    step_size: int, default None
        for the range_slider below the chart

    step_size_type: type, default int
        for the range_slider below the chart

    width: int,  default 800

    height: int,  default 400

    title: str,

        chart title

    timeout: int (milliseconds), default 100
        Determines the timeout after which the callback will
        process new events without the previous one having
        reported completion. Increase for very long running
        callbacks and if zooming feels laggy.

    legend: bool, default True
        Adds Bokeh.models.LinearColorMapper based legend if True,
        Note: legend currently only works with pixel_shade_type='linear'/'log'

    legend_position: str, default top_right
        position of legend on the chart.
        Valid places are: right, left, bottom, top, top_right, top_left,
                        bottom_left, bottom_right

    unselected_alpha: float [0, 1], default 0.2
        if True, displays unselected data in the same color_palette
        but transparent(alpha=0.2)

    **library_specific_params:
        additional library specific keyword arguments to be passed to the
        function

    Returns
    -------
    A cudashader stacked_lines plot of type:
        cuxfilter.charts.datashader.custom_extensions.InteractiveDatashaderMultiLine
    """
    if not isinstance(y, list) or len(y) == 0:
        raise ValueError("y must be a list of atleast one column name")
    plot = plots.StackedLines(
        x,
        y,
        data_points,
        add_interaction,
        colors,
        step_size,
        step_size_type,
        width,
        height,
        title,
        timeout,
        legend=legend,
        legend_position=legend_position,
        unselected_alpha=unselected_alpha,
        **library_specific_params,
    )
    plot.chart_type = "stacked_lines"
    return plot
