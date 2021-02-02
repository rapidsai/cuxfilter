import pytest

from cuxfilter.assets.numba_kernels import gpu_datatile
import numpy as np
import cudf
from numba import cuda
import pandas as pd
import bokeh
from cuxfilter.charts.core.core_chart import BaseChart


def test_calc_cumsum_data_tile():
    df = cudf.DataFrame(
        {
            "key": [float(i) for i in range(5)] * 5,
            "val": [float(i * 2) for i in range(5, 0, -1)] * 5,
        }
    )
    max_s = int(df["key"].max() - df["key"].min()) + 1
    min_s = int(df["val"].max() - df["val"].min()) + 1
    df["val_mod"] = ((df["val"] - df["val"].min()) / 1).round().astype("int32")
    groupby_as_ndarray = cuda.to_device(
        df.groupby(by=["key", "val_mod"], sort=True, as_index=False)
        .agg({"val": "count"})
        .to_pandas()
        .values.astype(float)
    )

    result = cuda.to_device(np.zeros(shape=(min_s, max_s)).astype(np.float64))

    assert np.array_equal(
        groupby_as_ndarray.copy_to_host(),
        np.array(
            [
                [0.0, 8.0, 5.0],
                [1.0, 6.0, 5.0],
                [2.0, 4.0, 5.0],
                [3.0, 2.0, 5.0],
                [4.0, 0.0, 5.0],
            ]
        ),
    )

    assert np.array_equal(
        result.copy_to_host(),
        np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
            ]
        ),
    )

    gpu_datatile.calc_cumsum_data_tile[64, 64](groupby_as_ndarray, result)

    assert np.array_equal(
        result.copy_to_host(),
        np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 5.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 5.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 5.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 5.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [5.0, 0.0, 0.0, 0.0, 0.0],
            ]
        ),
    )

    result_np = np.cumsum(result.copy_to_host(), axis=1)

    assert np.array_equal(
        result_np,
        np.array(
            [
                [0.0, 0.0, 0.0, 0.0, 5.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 5.0, 5.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 5.0, 5.0, 5.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 5.0, 5.0, 5.0, 5.0],
                [0.0, 0.0, 0.0, 0.0, 0.0],
                [5.0, 5.0, 5.0, 5.0, 5.0],
            ]
        ),
    )


@pytest.mark.parametrize(
    "result, return_format_str, return_format",
    [
        (
            np.array([[0.0, 0.0, 0.0, 0.0, 5.0], [0.0, 0.0, 0.0, 0.0, 0.0]]),
            "pandas",
            pd.core.frame.DataFrame,
        ),
        (
            np.array([[0.0, 0.0, 0.0, 0.0, 5.0], [0.0, 0.0, 0.0, 0.0, 0.0]]),
            "arrow",
            bytes,
        ),
        (
            np.array([[0.0, 0.0, 0.0, 0.0, 5.0], [0.0, 0.0, 0.0, 0.0, 0.0]]),
            "ColumnDataSource",
            bokeh.models.sources.ColumnDataSource,
        ),
    ],
)
def test_format_result(result, return_format_str, return_format):
    assert isinstance(
        gpu_datatile.format_result(result, return_format_str), return_format
    )


def test_calc_1d_data_tile():
    df = cudf.DataFrame(
        {
            "key": [float(i) for i in range(5)] * 5,
            "val": [float(i * 2) for i in range(5, 0, -1)] * 5,
        }
    )
    active_chart, passive_chart = BaseChart(), BaseChart()
    active_chart.x = "key"
    active_chart.min_value = df["key"].min()
    active_chart.max_value = df["key"].max()
    active_chart.stride = 1
    cumsum = True
    return_result = gpu_datatile.calc_1d_data_tile(
        df=df,
        active_view=active_chart,
        passive_view=passive_chart,
        cumsum=cumsum,
    )

    result = pd.DataFrame({0: {0: 5.0, 1: 10.0, 2: 15.0, 3: 20.0, 4: 25.0}})

    assert return_result.equals(result)


def test_calc_data_tile():
    df = cudf.DataFrame(
        {
            "key": [float(i) for i in range(5)] * 5,
            "val": [float(i * 2) for i in range(5, 0, -1)] * 5,
        }
    )
    active_chart, passive_chart = BaseChart(), BaseChart()
    active_chart.x, active_chart.min_value = "key", df["key"].min()
    active_chart.max_value, active_chart.stride = df["key"].max(), 1

    passive_chart.x, passive_chart.min_value = "val", df["val"].min()
    passive_chart.max_value, passive_chart.stride = df["val"].max(), 1

    cumsum = True
    return_result = gpu_datatile.calc_data_tile(
        df=df,
        active_view=active_chart,
        passive_view=passive_chart,
        cumsum=cumsum,
    )

    result = pd.DataFrame(
        {
            0: {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 0.0,
                7: 0.0,
                8: 5.0,
            },
            1: {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 0.0,
                5: 0.0,
                6: 5.0,
                7: 0.0,
                8: 5.0,
            },
            2: {
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: 5.0,
                5: 0.0,
                6: 5.0,
                7: 0.0,
                8: 5.0,
            },
            3: {
                0: 0.0,
                1: 0.0,
                2: 5.0,
                3: 0.0,
                4: 5.0,
                5: 0.0,
                6: 5.0,
                7: 0.0,
                8: 5.0,
            },
            4: {
                0: 5.0,
                1: 0.0,
                2: 5.0,
                3: 0.0,
                4: 5.0,
                5: 0.0,
                6: 5.0,
                7: 0.0,
                8: 5.0,
            },
        }
    )

    assert return_result.equals(result)
