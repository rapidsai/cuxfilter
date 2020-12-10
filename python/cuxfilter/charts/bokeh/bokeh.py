from . import plots


def bar(
    x,
    y=None,
    data_points=None,
    add_interaction=True,
    aggregate_fn="count",
    width=400,
    height=400,
    step_size=None,
    step_size_type=int,
    title="",
    autoscaling=True,
    **library_specific_params,
):
    """
    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    add_interaction: {True, False},  default True

    aggregate_fn: {'count', 'mean'},  default 'count'

    width: int,  default 400

    height: int,  default 400

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    title: str,

        chart title

    autoscaling: bool,

        set whether chart scale is updated automatically for
        y_axis when data updates

    x_label_map: dict,  default None
        label maps for x axis
        {value: mapped_str}
    y_label_map: dict,  default None
        label maps for y axis
        {value: mapped_str}

    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type vbar
    """
    plot = plots.Bar(
        x,
        y,
        data_points,
        add_interaction,
        aggregate_fn,
        width,
        height,
        step_size,
        step_size_type,
        title,
        autoscaling,
        **library_specific_params,
    )
    plot.chart_type = "bar"
    return plot


def line(
    x,
    y=None,
    data_points=None,
    add_interaction=True,
    aggregate_fn="count",
    width=400,
    height=400,
    step_size=None,
    step_size_type=int,
    title="",
    autoscaling=True,
    **library_specific_params,
):
    """

    Parameters
    ----------

    x: str
        x-axis column name from the gpu dataframe
    y: str, default None
        y-axis column name from the gpu dataframe
    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    add_interaction: {True, False},  default True

    aggregate_fn: {'count', 'mean'},  default 'count'

    width: int,  default 400

    height: int,  default 400

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    title: str,

        chart title

    autoscaling: bool,

        set whether chart scale is updated automatically
        for y_axis when data updates

    x_label_map: dict,  default None
        label maps for x axis
        {value: mapped_str}
    y_label_map: dict,  default None
        label maps for y axis
        {value: mapped_str}

    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type line
    """
    plot = plots.Line(
        x,
        y,
        data_points,
        add_interaction,
        aggregate_fn,
        width,
        height,
        step_size,
        step_size_type,
        title,
        autoscaling,
        **library_specific_params,
    )
    plot.chart_type = "line"
    return plot
