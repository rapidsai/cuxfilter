import pytest

from cuxfilter.assets import datetime as dt
from cuxfilter.charts.constants import CUDF_DATETIME_TYPES

import datetime
import pandas as pd
import cudf
import numpy as np


@pytest.mark.parametrize(
    "date, _type, factor",
    [
        (
            np.datetime64("2018-10-07").astype("datetime64[ns]"),
            "datetime64[ns]",
            1.0,
        ),
        (
            np.datetime64("2018-10-07").astype("datetime64[ns]"),
            "datetime64[ms]",
            1e-6,
        ),
        (
            np.datetime64("2018-10-07").astype("datetime64[s]"),
            "datetime64[ns]",
            1e9,
        ),
        (
            np.datetime64("2018-10-07").astype("datetime64[ns]"),
            "datetime64[s]",
            1e-9,
        ),
    ],
)
def test_get_dt_unit_factor(date, _type, factor):
    assert dt.get_dt_unit_factor(date, _type) == factor


@pytest.mark.parametrize(
    "date, result",
    [
        (1538870400, pd.to_datetime(1538870400, unit="s")),
        (1538870400000, pd.to_datetime(1538870400000, unit="ms")),
        (1538870400000000, pd.to_datetime(1538870400000000, unit="us")),
        (1538870400000000000, pd.to_datetime(1538870400000000000, unit="ns")),
    ],
)
def test_to_datetime(date, result):
    assert dt.to_datetime(date) == result


@pytest.mark.parametrize(
    "dates, _type, result_dates",
    [
        (
            (1538870400,),
            CUDF_DATETIME_TYPES[0],
            (datetime.datetime(2018, 10, 7, 0, 0),),
        ),
        (
            [datetime.datetime(2018, 10, 7, 0, 0)],
            CUDF_DATETIME_TYPES[1],
            [datetime.datetime(2018, 10, 7, 0, 0)],
        ),
        (
            [np.datetime64("2018-10-07T00:00:00.000000000")],
            CUDF_DATETIME_TYPES[1],
            [datetime.datetime(2018, 10, 7, 0, 0)],
        ),
    ],
)
def test_to_dt_if_datetime(dates, _type, result_dates):
    assert dt.to_dt_if_datetime(dates, _type) == result_dates


@pytest.mark.parametrize(
    "dates, _type, result_dates",
    [
        (
            (1538870400,),
            CUDF_DATETIME_TYPES[0],
            (np.datetime64("2018-10-07T00:00:00.000000000"),),
        ),
        (
            [datetime.datetime(2018, 10, 7, 0, 0)],
            CUDF_DATETIME_TYPES[1],
            [np.datetime64("2018-10-07T00:00:00.000000000")],
        ),
        (
            [np.datetime64("2018-10-07T00:00:00.000000000")],
            CUDF_DATETIME_TYPES[1],
            [np.datetime64("2018-10-07T00:00:00.000000000")],
        ),
    ],
)
def test_to_np_dt64_if_datetime(dates, _type, result_dates):
    assert dt.to_np_dt64_if_datetime(dates, _type) == result_dates


@pytest.mark.parametrize(
    "dates, _type, result_dates",
    [
        (
            cudf.Series(np.array(["2018-10-07"], dtype="datetime64")),
            "datetime64[ns]",
            cudf.Series(1.5388704e18).astype("int64"),
        ),
        (
            [np.datetime64("2018-10-07T00:00:00")],
            CUDF_DATETIME_TYPES[2],
            ([1.5388704e15]),
        ),
    ],
)
def test_to_int64_if_datetime(dates, _type, result_dates):
    assert (dt.to_int64_if_datetime(dates, _type) == result_dates).all()
