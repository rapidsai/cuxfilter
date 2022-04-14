from ctypes import ArgumentError
from .plots import (
    Card,
    NumberChart,
    RangeSlider,
    DateRangeSlider,
    IntSlider,
    FloatSlider,
    DropDown,
    MultiSelect,
    DataSizeIndicator,
)
from ..constants import CUDF_TIMEDELTA_TYPE


def range_slider(
    x,
    width=400,
    height=20,
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
        column name from gpu dataframe

    width: int,  default 400

    height: int,  default 20

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info


    """
    plot = RangeSlider(
        x, width, height, data_points, step_size, step_size_type, **params
    )
    plot.chart_type = "range_slider"
    return plot


def date_range_slider(
    x,
    width=400,
    height=20,
    data_points=None,
    **params,
):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: Range Slider

    Parameters
    ----------

    x: str
        column name from gpu dataframe

    width: int,  default 400

    height: int,  default 20

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: np.timedelta64, default np.timedelta64(days=1)

    **params:
        additional arguments to be passed to the function. See bokeh
        DateRangeSlider documentation for more info

    """
    plot = DateRangeSlider(
        x,
        width,
        height,
        data_points,
        step_size=None,
        step_size_type=CUDF_TIMEDELTA_TYPE,
        **params,
    )
    plot.chart_type = "date_range_slider"
    return plot


def int_slider(
    x, width=400, height=40, data_points=None, step_size=1, **params
):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: Int Slider

    Parameters
    ----------

    x: str
        column name from gpu dataframe

    width: int,  default 400

    height: int,  default 40

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: int,  default 1

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info


    """
    plot = IntSlider(
        x, width, height, data_points, step_size, step_size_type=int, **params
    )
    plot.chart_type = "int_slider"
    return plot


def float_slider(
    x, width=400, height=40, data_points=None, step_size=None, **params
):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: Float Slider

    Parameters
    ----------

    x: str
        column name from gpu dataframe

    width: int,  default 400

    height: int,  default 40

    data_points: int,  default None
        when None, it means no custom number of bins are provided and
        data_points will default to df[self.x].nunique()

    step_size: float,  default float((max - min)/datapoints)

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info


    """
    plot = FloatSlider(
        x,
        width,
        height,
        data_points,
        step_size,
        step_size_type=float,
        **params,
    )
    plot.chart_type = "float_slider"
    return plot


def drop_down(x, width=400, height=50, **params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: drop_down

    Parameters
    ----------

    x: str
        column name from gpu dataframe

    width: int,  default 400

    height: int,  default 50

    data_points: int,  default number of unique values

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info

    """
    plot = DropDown(x, width, height, **params)
    plot.chart_type = "dropdown"
    return plot


def multi_select(x, width=400, height=200, **params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: multi_select

    Parameters
    ----------

    x: str
        column name from gpu dataframe

    width: int,  default 400

    height: int,  default 200

    data_points: int,  default number of unique values

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info

    """
    plot = MultiSelect(x, width, height, **params)
    plot.chart_type = "multi_select"
    return plot


def data_size_indicator(**library_specific_params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: data_size_indicator

    Parameters
    ----------

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info

    """
    plot = DataSizeIndicator(
        title="Datapoints Selected", widget=True, **library_specific_params
    )
    plot.chart_type = "datasize_indicator"
    return plot


def number(
    x=None,
    expression=None,
    aggregate_fn="mean",
    title="",
    widget=True,
    format="{value}",
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
    x: str
        column name from gpu dataframe

    expression:
        string containing computable expression containing column names
        e.g: "(x+y)/2" will result in number value = (df.x + df.y)/2

    aggregate_fn: {'count', 'mean', 'min', 'max','sum', 'std'}, default 'count'

    title: str,
        chart title

    widget: bool, default True
        if widget is True, the chart gets placed on the side navbar,
        else its placed in the main dashboard

    format: str, default='{value}'
        A formatter string which accepts a {value}.

    colors: list
        Color thresholds for the Number indicator,
        specified as a tuple of the absolute thresholds and the color to
        switch to.
        e,g: colors=[(33, 'green'), (66, 'gold'), (100, 'red')]

    font_size: str, default '18pt'

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info

    """
    if not (x or expression):
        raise ArgumentError(
            "Atleast one of x or expression arg should be provided"
        )
    plot = NumberChart(
        x,
        expression,
        aggregate_fn,
        title,
        widget,
        format,
        colors,
        font_size,
        **library_specific_params,
    )
    return plot


def card(content="", title="", widget=True, **library_specific_params):
    """

    Card chart contating markdown content and can be located in either
    the main dashboard or side navbar.

    Type: number_chart or number_chart_widget

    Parameters
    ----------
    content: {str, markdown static content}, default ""

    title: str,
        chart title

    widget: bool, default True
        if widget is True, the chart gets placed on the side navbar,
        else its placed in the main dashboard

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info

    """
    return Card(content, title, widget, **library_specific_params)
