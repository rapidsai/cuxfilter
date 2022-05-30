import cudf
import dask_cudf
import gc
from typing import Type

from ...charts.core.core_chart import BaseChart


def calc_value_counts(
    a_gpu, stride, min_value, data_points, custom_binning=False
):
    """
    description:
        main function to calculate histograms
    input:
        - a_gpu: gpu array(cuda ndarray) -> 1-column only
        - bins: number of bins
    output:
        frequencies(ndarray), bin_edge_values(ndarray)
    """
    if isinstance(a_gpu, dask_cudf.core.Series):
        if not custom_binning:
            val_count = a_gpu.value_counts()
        else:
            val_count = (
                ((a_gpu - min_value) / stride)
                .round()
                .astype(a_gpu.dtype)
                .value_counts()
            )
        val_count = val_count.compute().sort_index()
    else:
        if not custom_binning:
            val_count = a_gpu.value_counts().sort_index()
        else:
            val_count = (
                ((a_gpu - min_value) / stride)
                .round()
                .astype(a_gpu.dtype)
                .value_counts()
                .sort_index()
            )

    return (
        (val_count.index.values_host, val_count.values_host),
        len(val_count),
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
        if isinstance(temp_df, dask_cudf.core.DataFrame):
            groupby_res = getattr(
                temp_df.groupby(by=[chart.x], sort=True), chart.aggregate_fn
            )()
            groupby_res = groupby_res.reset_index().compute()
        else:
            groupby_res = temp_df.groupby(
                by=[chart.x], sort=True, as_index=False
            ).agg({chart.y: chart.aggregate_fn})
    else:
        for key, agg_fn in agg.items():
            temp_df[key] = data[key]
        if isinstance(data, dask_cudf.core.DataFrame):
            groupby_res = None
            for key, agg_fn in agg.items():
                groupby_res_temp = getattr(
                    temp_df[[chart.x, key]].groupby(chart.x, sort=True), agg_fn
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
            groupby_res = groupby_res
        else:
            groupby_res = temp_df.groupby(
                by=[chart.x], sort=True, as_index=False
            ).agg(agg)

    del temp_df
    gc.collect()

    return groupby_res


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
    temp_df[chart.x] = (data[chart.x] / chart.stride) - chart.min_value
    return temp_df[chart.x].unique().to_pandas().tolist()
