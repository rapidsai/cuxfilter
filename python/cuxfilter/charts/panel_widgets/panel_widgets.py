# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from .plots import (
    Card,
    NumberChart,
    RangeSlider,
    DateRangeSlider,
    IntSlider,
    FloatSlider,
    MultiChoice,
    DataSizeIndicator,
)
from ..constants import CUDF_TIMEDELTA_TYPE


def range_slider(
    x,
    data_points=None,
    step_size=None,
    step_size_type=int,
    **params,
):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: Range Slider

    Parameters
    ----------

    x: str
        column name from gpu dataframe, dtype should be int or float

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/widgets/RangeSlider.html#parameters


    """
    plot = RangeSlider(x, data_points, step_size, step_size_type, **params)
    plot.chart_type = "range_slider"
    return plot


def date_range_slider(
    x,
    data_points=None,
    **params,
):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: Range Slider

    Parameters
    ----------

    x: str
        column name from gpu dataframe, dtype should be datetime

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: np.timedelta64, default np.timedelta64(days=1)

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/widgets/DateRangeSlider.html#parameters

    """
    plot = DateRangeSlider(
        x,
        data_points,
        step_size=None,
        step_size_type=CUDF_TIMEDELTA_TYPE,
        **params,
    )
    plot.chart_type = "date_range_slider"
    return plot


def int_slider(x, data_points=None, step_size=1, **params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: Int Slider

    Parameters
    ----------

    x: str
        column name from gpu dataframe, dtype should be int

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: int,  default 1

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/widgets/IntSlider.html#parameters

    """
    plot = IntSlider(x, data_points, step_size, step_size_type=int, **params)
    plot.chart_type = "int_slider"
    return plot


def float_slider(x, data_points=None, step_size=None, **params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: Float Slider

    Parameters
    ----------

    x: str
        column name from gpu dataframe, dtype should be float

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: float,  default float((max - min)/datapoints)

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/widgets/FloatSlider.html#parameters

    """
    plot = FloatSlider(
        x,
        data_points,
        step_size,
        step_size_type=float,
        **params,
    )
    plot.chart_type = "float_slider"
    return plot


def drop_down(x, **params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: drop_down

    Parameters
    ----------

    x: str
        column name from gpu dataframe, dtype [str, int, float]

    data_points: int,  default number of unique values

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/widgets/MultiChoice.html#parameters

    """
    plot = MultiChoice(x, max_items=1, **params)
    plot.chart_type = "dropdown"
    return plot


def multi_select(x, **params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: multi_choice

    Parameters
    ----------

    x: str
        column name from gpu dataframe, dtype [str, int, float]

    data_points: int,  default number of unique values

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/widgets/MultiChoice.html#parameters

    """
    plot = MultiChoice(x, **params)
    plot.chart_type = "multi_choice"
    return plot


def data_size_indicator(title_size="14pt"):
    """

    Data size indicator widget in the navbar of the cuxfilter dashboard.
    Returns a DataSizeIndicator widget, which is used display the current data
    size. For custom number widget, use the cuxfilter.widgets.number.

    Type: data_size_indicator
    """
    plot = DataSizeIndicator(
        title="Datapoints Selected", widget=True, title_size=title_size
    )
    plot.chart_type = "datasize_indicator"
    return plot


def number(
    expression,
    aggregate_fn="mean",
    title="",
    format="{value}",
    default_color="black",
    colors=[],
    font_size="18pt",
    **library_specific_params,
):
    """

    Number chart which can be located in either the main dashboard or
    side navbar.

    Type: number_chart or number_chart_widget

    Parameters
    ----------
    expression:
        string containing computable expression containing column names
        e.g: "(x+y)/2" will result in number value = (df.x + df.y)/2

    aggregate_fn: {'count', 'mean', 'min', 'max','sum', 'std'}, default 'count'

    title: str,
        chart title

    format: str, default='{value}'
        A formatter string which accepts a {value}.

    default_color: str, default 'black'
        A color string to use as the default color if no thresholds are passed
        via the colors argument.

    colors: list
        Color thresholds for the Number indicator,
        specified as a tuple of the absolute thresholds and the color to
        switch to.
        e,g: colors=[(33, 'green'), (66, 'gold'), (100, 'red')]

    font_size: str, default '18pt'

    title_size: str, default '14pt'

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/indicators/Number.html#parameters
    """
    plot = NumberChart(
        expression=expression,
        aggregate_fn=aggregate_fn,
        title=title,
        format=format,
        default_color=default_color,
        colors=colors,
        font_size=font_size,
        **library_specific_params,
    )
    plot.chart_type = "number"
    return plot


def card(content="", **library_specific_params):
    """

    Card chart contating markdown content and can be located in either
    the main dashboard or side navbar.

    Type: number_chart

    Parameters
    ----------
    content: {str, markdown static content}, default ""

    **params:
        additional arguments to be passed to the function. See panel widgets
        documentation for more info,
        https://panel.holoviz.org/reference/layouts/Card.html#parameters

    """
    return Card(content, **library_specific_params)
