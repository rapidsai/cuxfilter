from .plots import (
    RangeSlider,
    IntSlider,
    FloatSlider,
    DropDown,
    MultiSelect,
    DataSizeIndicator,
)


def range_slider(
    x,
    width=400,
    height=20,
    data_points=100,
    step_size=1,
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

    data_points: int,  default 100

    step_size: int,  default 1

    step_size_type: {int, float},  default int

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info


    """
    return RangeSlider(
        x, width, height, data_points, step_size, step_size_type, **params
    )


def int_slider(
    x, width=400, height=40, data_points=100, step_size=1, **params
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

    data_points: int,  default 100

    step_size: int,  default 1

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info


    """
    return IntSlider(
        x, width, height, data_points, step_size, step_size_type=int, **params
    )


def float_slider(
    x, width=400, height=40, data_points=100, step_size=None, **params
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

    data_points: int,  default 100

    step_size: float,  default float((max - min)/datapoints)

    **params:
        additional arguments to be passed to the function. See panel
        documentation for more info


    """
    return FloatSlider(
        x,
        width,
        height,
        data_points,
        step_size,
        step_size_type=float,
        **params,
    )


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
    return DropDown(x, width, height, **params)


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
    return MultiSelect(x, width, height, **params)


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
    return DataSizeIndicator(width, height, **library_specific_params)
