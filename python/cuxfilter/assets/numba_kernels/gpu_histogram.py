import numpy as np
from numba import cuda
import cudf
import dask_cudf
import numba
import gc
from typing import Type

from ...charts.core.core_chart import BaseChart


def calc_value_counts(a_gpu, stride, min_value, data_points):
    """
    description:
        main function to calculate histograms
    input:
        - a_gpu: gpu array(cuda ndarray) -> 1-column only
        - bins: number of bins
    output:
        frequencies(ndarray), bin_edge_values(ndarray)
    """
    if type(a_gpu) == dask_cudf.core.Series:
        if data_points == a_gpu.nunique().compute():
            val_count = a_gpu.value_counts()
        else:
            val_count = ((a_gpu / stride) - min_value).value_counts()
        val_count = val_count.compute().sort_index()
    else:
        if data_points == a_gpu.nunique():
            val_count = a_gpu.value_counts().sort_index()
        else:
            val_count = ((a_gpu / stride) - min_value).value_counts()

    return val_count.index.to_array(), val_count.to_array()


def calc_groupby(chart: Type[BaseChart], data, agg=None):
    """
    description:
        main function to calculate histograms
    input:
        - chart
        - data
    output:
        frequencies(ndarray), bin_edge_values(ndarray)
    """

    if agg is None:
        temp_df = cudf.DataFrame()
        temp_df.index = data.dropna(subset=[chart.x]).index
        temp_df.add_column(
            chart.x,
            (data[chart.x] / chart.stride) - chart.min_value,
        )
        temp_df.add_column(
            chart.y, data.dropna(subset=[chart.x])[chart.y].copy()
        )
        if type(data) == dask_cudf.core.DataFrame:
            groupby_res = (
                temp_df.groupby(by=[chart.x], as_index=False)
                .agg({chart.y: chart.aggregate_fn})
                .to_pandas()
            )
        del temp_df
        gc.collect()
    else:
        groupby_res = (
            data.groupby(by=[chart.x], as_index=False).agg(agg).to_pandas()
        )
    return groupby_res.to_numpy().transpose()


def aggregated_column_unique(chart: Type[BaseChart], data):
    """
    description:
        main function to calculate histograms
    input:
        - chart
        - data
    output:
        list_of_unique_values
    """

    a_range = cuda.to_device(np.array([chart.min_value, chart.max_value]))
    temp_df = cudf.DataFrame()
    temp_df.add_column(
        chart.x,
        get_binwise_reduced_column(
            data[chart.x].copy().to_gpu_array(), chart.stride, a_range
        ),
    )
    return temp_df[chart.x].unique().to_pandas().tolist()
