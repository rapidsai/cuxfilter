# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from argparse import ArgumentError

from .plots import Bar, Histogram


def bar(
    x,
    y=None,
    data_points=None,
    add_interaction=True,
    aggregate_fn=None,
    step_size=None,
    step_size_type=int,
    title="",
    autoscaling=True,
    unselected_alpha=0.1,
    **library_specific_params,
):
    """
    Create a bar chart or histogram using Bokeh backend.

    Parameters
    ----------
    x : str
        x-axis column name from the gpu dataframe
    y : str
        y-axis column name from the gpu dataframe
    data_points : int
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()
    add_interaction : {True, False}
        whether to add selection interaction to the chart
    aggregate_fn : {'count', 'mean'}
        aggregation function to apply when y is provided
    step_size : int
        step size for binning data
    step_size_type : {int, float}
        type of step size for binning
    title : str
        chart title
    autoscaling : bool
        set whether chart scale is updated automatically for y_axis when data
        updates
    unselected_alpha : float
        alpha value for unselected data points
    **library_specific_params
        additional library specific keyword arguments to be passed to
        the function, a list of all the supported arguments can be found by
        running:

            >>> import holoviews as hv
            >>> hv.help(hv.Bars)

    Returns
    -------
    Bar or Histogram
        A bokeh chart object of type vbar (Bar) or histogram (Histogram)
    """

    if y is not None:
        plot = Bar(
            x=x,
            y=y,
            data_points=data_points,
            add_interaction=add_interaction,
            aggregate_fn=aggregate_fn or "mean",
            step_size=step_size,
            step_size_type=step_size_type,
            title=title,
            autoscaling=autoscaling,
            unselected_alpha=unselected_alpha,
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
            step_size=step_size,
            step_size_type=step_size_type,
            title=title,
            autoscaling=autoscaling,
            unselected_alpha=unselected_alpha,
            **library_specific_params,
        )
        plot.chart_type = "histogram"
    return plot
