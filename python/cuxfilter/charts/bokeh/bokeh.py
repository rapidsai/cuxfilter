from .plots import Bar, Histogram


def bar(
    x,
    y=None,
    data_points=None,
    add_interaction=True,
    aggregate_fn=None,
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

    **library_specific_params:
        additional library specific keyword arguments to be passed to
        the function

    Returns
    -------
    A bokeh chart object of type vbar
    """

    if y is not None:
        plot = Bar(
            x=x,
            y=y,
            data_points=data_points,
            add_interaction=add_interaction,
            aggregate_fn=aggregate_fn or "mean",
            width=width,
            height=height,
            step_size=step_size,
            step_size_type=step_size_type,
            title=title,
            autoscaling=autoscaling,
            **library_specific_params,
        )
        plot.chart_type = "bar"
    else:
        if aggregate_fn:
            raise ArgumentError(
                "`y` should be provided when aggregate_fn is provided",
                " else a histogram is plotted",
            )
        plot = Histogram(
            x=x,
            data_points=data_points,
            add_interaction=add_interaction,
            width=width,
            height=height,
            step_size=step_size,
            step_size_type=step_size_type,
            title=title,
            autoscaling=autoscaling,
            **library_specific_params,
        )
        plot.chart_type = "histogram"
    return plot
