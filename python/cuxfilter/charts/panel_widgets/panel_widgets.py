from .plots import (
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
    plot.chart_type = "widget_range_slider"
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
    plot.chart_type = "widget_date_range_slider"
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
    plot.chart_type = "widget_int_slider"
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
    plot.chart_type = "widget_float_slider"
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
    plot.chart_type = "widget_dropdown"
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
    plot.chart_type = "widget_multi_select"
    return plot


def data_size_indicator(width=400, height=50, **library_specific_params):
    """

    Widget in the navbar of the cuxfilter dashboard.

    Type: data_size_indicator

    Parameters
    ----------

    width: int,  default 400

    height: int,  default 200

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info

    """
    plot = DataSizeIndicator(width, height, **library_specific_params)
    plot.chart_type = "datasize_indicator"
    return plot
