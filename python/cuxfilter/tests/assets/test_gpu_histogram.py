import pytest

from cuxfilter.assets.numba_kernels import gpu_histogram
import cudf
import numpy as np
from numba import cuda

from cuxfilter.charts.core.core_chart import BaseChart


def test_calc_value_counts():
    x = cudf.Series(
        np.array(
            [
                1,
                5,
                10,
                15,
                25,
                27,
                30,
                23,
                22,
                35,
                39,
                99,
                109,
                109,
                104,
                11,
                23,
            ]
            * 50
        )
    )
    bins = 8
    stride = (x.max() - x.min()) / bins

    result, data_points, custom_binning = gpu_histogram.calc_value_counts(
        x, stride, x.min(), None
    )
    assert np.array_equal(result[0], np.array([0, 1, 2, 3, 7, 8]))
    assert np.array_equal(result[1], np.array([100, 150, 300, 100, 50, 150]))
    assert data_points == 6
    assert custom_binning is True


@pytest.mark.parametrize(
    "aggregate_fn, result",
    [
        (
            "count",
            np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [5.0, 5.0, 5.0, 5.0, 5.0]]),
        ),
        (
            "mean",
            np.array([[0.0, 1.0, 2.0, 3.0, 4.0], [10.0, 8.0, 6.0, 4.0, 2.0]]),
        ),
    ],
)
def test_calc_groupby(aggregate_fn, result):
    df = cudf.DataFrame(
        {
            "key": [float(i) for i in range(5)] * 5,
            "val": [float(i * 2) for i in range(5, 0, -1)] * 5,
        }
    )
    bc = BaseChart()
    bc.x = "key"
    bc.y = "val"
    bc.stride = 1.0
    bc.max_value = 4.0
    bc.min_value = 0.0
    bc.data_points = 25

    bc.aggregate_fn = aggregate_fn

    assert np.array_equal(gpu_histogram.calc_groupby(bc, df), result)


@pytest.mark.parametrize(
    "x, y, aggregate_fn, result",
    [
        ("key", "val", "mean", np.array([[1.0, 2.0], [np.NaN, 3.0]])),
        ("val", "key", "mean", np.array([[3.0], [2.0]])),
    ],
)
def test_calc_groupby_for_nulls(x, y, aggregate_fn, result):
    df = cudf.DataFrame({"key": [1, 2], "val": [np.NaN, 3]})
    print(df, x, y)
    bc = BaseChart()
    bc.x = x
    bc.y = y
    bc.stride = 1.0
    bc.min_value = df[x].min()
    bc.max_value = df[x].max()
    bc.aggregate_fn = aggregate_fn
    print(gpu_histogram.calc_groupby(bc, df))
    print(result)
    assert np.allclose(
        gpu_histogram.calc_groupby(bc, df), result, equal_nan=True
    )


def test_aggregated_column_unique():
    df = cudf.DataFrame(
        {
            "key": cuda.to_device(
                np.array(
                    [
                        1,
                        5,
                        10,
                        15,
                        25,
                        27,
                        30,
                        23,
                        22,
                        35,
                        39,
                        99,
                        109,
                        109,
                        104,
                        11,
                        23,
                    ]
                    * 50
                )
            )
        }
    )
    bc = BaseChart()
    bc.x = "key"
    bc.stride = 1.0
    bc.max_value = df["key"].max()
    bc.min_value = df["key"].min()

    assert np.array_equal(
        gpu_histogram.aggregated_column_unique(bc, df),
        np.array([0, 4, 9, 10, 14, 21, 22, 24, 26, 29, 34, 38, 98, 103, 108]),
    )
