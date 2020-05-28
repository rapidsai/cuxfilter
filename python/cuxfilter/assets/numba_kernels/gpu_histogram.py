import cudf
import dask_cudf
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
    custom_binning = False
    if type(a_gpu) == dask_cudf.core.Series:
        if stride is None or a_gpu.dtype == 'bool':
            val_count = a_gpu.value_counts()
        else:
            val_count = (
                ((a_gpu - min_value) / stride)
                .round()
                .astype(a_gpu.dtype)
                .value_counts()
            )
            custom_binning = True
        val_count = val_count.compute().sort_index()
    else:
        if stride is None or a_gpu.dtype == 'bool':
            val_count = a_gpu.value_counts().sort_index()
        else:
            val_count = (
                ((a_gpu - min_value) / stride)
                .round()
                .astype(a_gpu.dtype)
                .value_counts()
                .sort_index()
            )
            custom_binning = True

    return (
        (val_count.index.to_array(), val_count.to_array()),
        len(val_count),
        custom_binning,
    )


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
    temp_df = data[[chart.x]].dropna(subset=[chart.x])

    if agg is None:
        temp_df[chart.y] = data.dropna(subset=[chart.x])[chart.y]
        if type(temp_df) == dask_cudf.core.DataFrame:
            groupby_res = getattr(
                temp_df.groupby(by=[chart.x]), chart.aggregate_fn
            )()
            groupby_res = groupby_res.reset_index().compute().to_pandas()
        else:
            groupby_res = (
                temp_df.groupby(by=[chart.x], as_index=False)
                .agg({chart.y: chart.aggregate_fn})
                .to_pandas()
            )
    else:
        for key, agg_fn in agg.items():
            temp_df[key] = data[key]
        if type(data) == dask_cudf.core.DataFrame:
            groupby_res = None
            for key, agg_fn in agg.items():
                groupby_res_temp = getattr(
                    temp_df[[chart.x, key]].groupby(chart.x), agg_fn
                )()
                if groupby_res is None:
                    groupby_res = groupby_res_temp.reset_index().compute()
                else:
                    groupby_res_temp = groupby_res_temp.reset_index().compute()
                    groupby_res = groupby_res.merge(
                        groupby_res_temp, on=chart.x
                    )
                del groupby_res_temp
                gc.collect()
            groupby_res = groupby_res.to_pandas()
        else:
            groupby_res = (
                temp_df.groupby(by=[chart.x], as_index=False)
                .agg(agg)
                .to_pandas()
            )

    del temp_df
    gc.collect()

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

    temp_df = cudf.DataFrame()
    temp_df.add_column(
        chart.x, (data[chart.x] / chart.stride) - chart.min_value
    )
    return temp_df[chart.x].unique().to_pandas().tolist()
