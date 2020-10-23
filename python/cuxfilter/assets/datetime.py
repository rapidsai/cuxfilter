import numpy as np
import cupy as cp
import pandas as pd
import datetime
import cudf
import math

from ..charts.constants import CUDF_DATETIME_TYPES, CUDF_TIMEDELTA_TYPE

dt = {
    CUDF_DATETIME_TYPES[0]: 9,
    CUDF_DATETIME_TYPES[1]: 12,
    CUDF_DATETIME_TYPES[2]: 15,
    CUDF_DATETIME_TYPES[3]: 18,
}

dt_unit = {9: "s", 12: "ms", 15: "us", 18: "ns"}


def date_to_int(date):
    if type(date) == np.datetime64:
        date = date.astype("int64")
    return date


def get_dt_unit_factor(date, _type):
    if type(date) == datetime.datetime:
        date = date.timestamp()

    _pow = dt[str(_type)] - int(math.log10(date_to_int(date)))
    return math.pow(10, _pow)


def to_datetime(dates):
    """
    Description:
        Convert dates to pd.to_datetime while also figuring out
        date_type unit
    -------------------------------------------
    Input:
        dates = list or tuple of dates
    -------------------------------------------
    Output:
        pd.to_datetime object
    """
    unit = {}
    test_date = dates[0] if type(dates) in [list, tuple, pd.Series] else dates
    if type(test_date) != datetime.datetime:
        unit["unit"] = dt_unit[int(math.log10(date_to_int(test_date)))]
    return pd.to_datetime(dates, **unit)


def to_dt_if_datetime(dates, _type):
    """
    Description:
        convert to datetime.datetime if _type in CUDF_DATETIME_TYPES

    -------------------------------------------
    Input:
        dates = list or tuple of integer timestamps objects
        _type = dtype
    -------------------------------------------

    Ouput:
        list of datetime.datetime objects
    """
    if _type in CUDF_DATETIME_TYPES and type(dates) in [list, tuple]:
        return type(dates)(to_datetime(dates).to_pydatetime())
    return dates


def to_np_dt64_if_datetime(dates, _type):
    """
    Description:
        convert to np.datetime64 if _type in CUDF_DATETIME_TYPES

    -------------------------------------------
    Input:
        dates = list or tuple of datetime.datetime objects
        _type = dtype
    -------------------------------------------

    Ouput:
        list of np.datetime64 objects

    """
    if _type in CUDF_DATETIME_TYPES and type(dates) in [list, tuple]:
        dates = to_datetime(dates)
        return type(dates)([date.to_datetime64() for date in dates])
    return dates


def check_series_for_nan(ser_):
    if ser_.dtype == "float64":
        return ser_[~cp.isnan(ser_)].shape[0] > 0
    return True


def to_int64_if_datetime(dates, _type):
    """
    Description:
        convert to int64 for input to datashader based plots
    -------------------------------------------
    Input:
        col: cudf.Series | list | tuple
        _type: cudf.dtype
    """
    if _type in CUDF_DATETIME_TYPES:
        if type(dates) in [list, tuple]:
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(dates[0], _type)
            return (np.array(dates).astype("int64")) * dt_s_factor
        elif type(dates) == cudf.Series and check_series_for_nan(dates):
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(dates.iloc[0], _type)
            return (dates.astype("int64")) * dt_s_factor
    return dates


def transform_stride_type(stride_type, _type):
    if _type in CUDF_DATETIME_TYPES:
        return CUDF_TIMEDELTA_TYPE
    return stride_type
