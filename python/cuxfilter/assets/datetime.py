import numpy as np
import cudf
import math

from ..charts.constants import CUDF_DATETIME_TYPES, CUDF_TIMEDELTA_TYPE

dt = {
    CUDF_DATETIME_TYPES[0]: 9,
    CUDF_DATETIME_TYPES[1]: 12,
    CUDF_DATETIME_TYPES[2]: 15,
    CUDF_DATETIME_TYPES[3]: 18,
}


def get_dt_unit_factor(date, _type):
    _pow = dt[str(_type)] - int(math.log10(date))
    return math.pow(10, _pow)


def to_dt64_if_datetime(dates, _type):
    """
    convert to datetime if _type in CUDF_DATETIME_TYPES
    """
    if _type in CUDF_DATETIME_TYPES:
        if (
            type(dates) in [list, tuple]
            and type(dates[0]) not in CUDF_DATETIME_TYPES
        ):
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(int(dates[0]), _type)
            return (np.array(dates) * dt_s_factor).astype(_type)
        elif (
            type(dates) == cudf.Series
            and dates.dtype not in CUDF_DATETIME_TYPES
        ):
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(dates.iloc[0], _type)
            return (dates * dt_s_factor).astype(_type)

    return dates


def to_int64_if_datetime(dates, _type):
    """
    col: cudf.Series | list | tuple
    _type: cudf.dtype
    """
    if _type in CUDF_DATETIME_TYPES:
        if type(dates) in [list, tuple]:
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(int(dates[0]), _type)
            return (np.array(dates).astype("int64")) * dt_s_factor
        elif type(dates) == cudf.Series:
            # compute date seconds factor
            dt_s_factor = get_dt_unit_factor(int(dates.iloc[0]), _type)
            return (dates.astype("int64")) * dt_s_factor
    return dates


def transform_stride_type(stride_type, _type):
    if _type in CUDF_DATETIME_TYPES:
        return CUDF_TIMEDELTA_TYPE
    return stride_type
