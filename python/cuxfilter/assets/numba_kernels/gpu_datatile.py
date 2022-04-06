import numpy as np
from numba import cuda
import pyarrow as pa
import pandas as pd
import io
import gc
from bokeh.models import ColumnDataSource
from typing import Type
import dask_cudf

from ...charts.core.core_chart import BaseChart


@cuda.jit
def calc_cumsum_data_tile(x, arr1):
    """
    description:
        cuda jit function calculate the data tile with cumulative sums
        for a 2-col ndarray
    input:
        - x: ndarray(3-cols)  (col1,col2, count_col2)
        - arr1: result array: type is int as the cells contain just
        frequencies
        (cuda.to_device(np.zeros(shape=(min_s,max_s)).astype(np.int32)))
        [X X X]
        [X X X]
        [X X X]
    """
    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    for i in range(start, x.shape[0], stride):
        col1_i = int(round(x[i][0]))
        col2_i = int(round(x[i][1]))
        freq_i = x[i][2]

        if int(x[i][0]) != -1:
            if arr1[col2_i][col1_i] == float(0):
                arr1[col2_i][col1_i] = freq_i
            else:
                arr1[col2_i][col1_i] = (arr1[col2_i][col1_i] + freq_i) / 2


def get_arrow_stream(record_batch):
    outputStream = io.BytesIO()
    writer = pa.ipc.RecordBatchStreamWriter(outputStream, record_batch.schema)
    writer.write_batch(record_batch)
    writer.close()
    return outputStream.getvalue()


def format_result(result_np: np.ndarray, return_format: str):
    """
    format result as a pandas dataframe
    """
    pandas_df = pd.DataFrame(result_np, dtype=np.float64)

    if return_format == "pandas":
        return pandas_df

    elif return_format == "arrow":
        result_pa = pa.RecordBatch.from_pandas(pandas_df, preserve_index=True)
        return get_arrow_stream(result_pa)

    elif return_format == "ColumnDataSource":
        pandas_df.columns = pandas_df.columns.astype(str)
        return ColumnDataSource(pandas_df)


def calc_1d_data_tile(
    df,
    active_view: Type[BaseChart],
    passive_view: Type[BaseChart],
    cumsum: bool = True,
    return_format="pandas",
):
    col_1, min_1, max_1, stride_1 = (
        active_view.x,
        active_view.min_value,
        active_view.max_value,
        active_view.stride,
    )
    if passive_view.x:
        col_2 = passive_view.x
        columns = [f"{col_1}_mod", col_2]
    else:
        col_2 = f"{col_1}_mod"
        columns = [col_2]

    aggregate_fn = passive_view.aggregate_fn

    df[columns[0]] = ((df[col_1] - min_1) / stride_1).round().astype("int32")
    if isinstance(df, dask_cudf.core.DataFrame):
        groupby_result = getattr(
            df[columns + [col_1]].groupby(columns[0]), aggregate_fn
        )().compute()
    else:
        groupby_result = (
            df[columns]
            .groupby(columns[0], as_index=True)
            .agg({col_2: aggregate_fn})
        )

    max_s = int(round((max_1 - min_1) / stride_1)) + 1
    min_s = 1

    result = np.zeros(shape=(min_s, max_s)).astype(np.float64)[0]

    groupby_result_array_index = groupby_result.index.values_host.astype(int)
    groupby_result_array = groupby_result[
        groupby_result.columns[-1]
    ].values_host

    del groupby_result

    for index, value in np.ndenumerate(groupby_result_array_index):
        result[value] = groupby_result_array[index[0]]

    if cumsum:
        result_np = np.cumsum(result)
    else:
        result_np = result
    return format_result(result_np, return_format)


def calc_data_tile(
    df,
    active_view: Type[BaseChart],
    passive_view: Type[BaseChart],
    aggregate_fn: str = "",
    cumsum: bool = True,
    return_format="pandas",
):
    """
    description:
        cuda jit function calculate the data tile with cumulative sums for a
        2-col ndarray
    input:
        - df -> cudf dataframe
        - active_view -> chart class
        - passive_view -> chart class
        - aggregate_dict
        - cumsum: bool
        - return_format: pandas/arrow/bokeh.models.ColumnDataSource
    output:
        - pyarrow(2d-numpy array) -> data-tile data structure
    """

    col_1, min_1, max_1, stride_1 = (
        active_view.x,
        active_view.min_value,
        active_view.max_value,
        active_view.stride,
    )
    col_2, min_2, max_2, stride_2 = (
        passive_view.x,
        passive_view.min_value,
        passive_view.max_value,
        passive_view.stride,
    )

    key = passive_view.y if passive_view.y is not None else passive_view.x
    if len(aggregate_fn) == 0:
        aggregate_fn = passive_view.aggregate_fn

    if aggregate_fn == "mean":
        aggregate_dict = {key: ["sum", "count"]}
    else:
        aggregate_dict = {key: [aggregate_fn]}

    check_list = []

    df[col_1 + "_mod"] = (
        ((df[col_1] - min_1) / stride_1).round().astype("int32")
    )
    check_list.append(col_1 + "_mod")
    df[col_2 + "_mod"] = (
        ((df[col_2] - min_2) / stride_2).round().astype("int32")
    )
    check_list.append(col_2 + "_mod")

    groupby_results = []
    for i in aggregate_dict[key]:
        agg = {key: i}
        if isinstance(df, dask_cudf.core.DataFrame):
            temp_df = getattr(
                df[check_list + [key]].groupby(check_list, sort=False), i
            )()
            temp_df = temp_df.reset_index().compute()
            groupby_results.append(temp_df)
        else:
            groupby_results.append(
                df.groupby(check_list, sort=False, as_index=False).agg(agg)
            )

    del df
    gc.collect()

    results = []

    for groupby_result in groupby_results:
        list_of_indices = list(
            np.unique(groupby_result[check_list[-1]].values_host.astype(int))
        )
        groupby_as_ndarray = cuda.to_device(
            groupby_result.to_pandas().values.astype(float)
        )

        del groupby_result
        gc.collect()
        max_s = int(round((max_1 - min_1) / stride_1)) + 1
        min_s = int(round((max_2 - min_2) / stride_2)) + 1
        result = cuda.to_device(
            np.zeros(shape=(min_s, max_s)).astype(np.float64)
        )

        calc_cumsum_data_tile[64, 64](groupby_as_ndarray, result)
        if not cumsum:
            result_np = result.copy_to_host()
        else:
            result_np = np.cumsum(result.copy_to_host(), axis=1)

        result_temp = format_result(result_np, return_format)
        if return_format == "pandas":
            result_temp[~result_temp.index.isin(list_of_indices)] = 0
        results.append(result_temp)

    if len(results) == 1:
        return results[0]

    return results
