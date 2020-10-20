import numpy as np
import cupy as cp
import pandas as pd
import cudf
import math

from ..charts.constants import CUDF_DATETIME_TYPES, CUDF_TIMEDELTA_TYPE

dt = {
    CUDF_DATETIME_TYPES[0]: 9,
    CUDF_DATETIME_TYPES[1]: 12,
    CUDF_DATETIME_TYPES[2]: 15,
    CUDF_DATETIME_TYPES[3]: 18,
}

dt_unit = {
    9: 's',
    12: 'ms',
    15: 'us',
    18: 'ns'
}


def get_dt_unit_factor(date, _type):
    _pow = dt[str(_type)] - int(math.log10(date))
    return math.pow(10, _pow)


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
    if _type in CUDF_DATETIME_TYPES:
        if type(dates) in [list, tuple]:
            # compute date seconds factor
            if type(dates[0]) in [int, float]:
                dates = pd.to_datetime(
                    dates, unit=dt_unit[int(math.log10(dates[0]))]
                )
            else:
                dates = pd.to_datetime(dates)

            return dates.to_pydatetime()
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
    if _type in CUDF_DATETIME_TYPES:
        dates = pd.to_datetime(dates)
        return [date.to_datetime64() for date in dates]

    return dates


def check_series_for_nan(ser_):
    if ser_.dtype == 'float64':
        return ser_[~cp.isnan(ser_)].shape[0] > 0
    return True


def to_int64_if_datetime(dates, _type):
    """
    col: cudf.Series | list | tuple
    _type: cudf.dtype
    """
    if _type in CUDF_DATETIME_TYPES:
        if type(dates) in [list, tuple]:
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(dates[0], _type)
            return (np.array(dates).astype("int64")) * dt_s_factor
        elif(
            type(dates) == cudf.Series and check_series_for_nan(dates)
        ):
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(
                dates.iloc[0], _type
            )
            return (dates.astype("int64")) * dt_s_factor
    return dates


def transform_stride_type(stride_type, _type):
    if _type in CUDF_DATETIME_TYPES:
        return CUDF_TIMEDELTA_TYPE
    return stride_type
