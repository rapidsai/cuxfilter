import numpy as np
from numba import cuda
import numba
import pyarrow as pa
import pandas as pd
import io
import gc
from bokeh.models import ColumnDataSource
from typing import Type, Tuple

from ...charts.core.core_chart import BaseChart


@cuda.jit
def calc_cumsum_data_tile(x, arr1):
    '''
    description:
        cuda jit function calculate the data tile with cumulative sums for a 2-col ndarray
    input:
        - x: ndarray(3-cols)  (col1,col2, count_col2)
        - arr1: result array: type is int as the cells contain just frequencies (cuda.to_device(np.zeros(shape=(min_s,max_s)).astype(np.int32)))
        [X X X]
        [X X X]
        [X X X]
    '''
    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    for i in range(start, x.shape[0], stride):
        if int(x[i][0]) != -1:
            if arr1[int(x[i][1])][int(x[i][0])] == float(0):
                arr1[int(x[i][1])][int(x[i][0])] = x[i][2]
            else:
                arr1[int(x[i][1])][int(x[i][0])] = (arr1[int(x[i][1])][int(x[i][0])]+x[i][2])/2

@cuda.jit
def calc_binwise_reduced_column(x, stride, a_range):
    '''
    description:
        cuda jit for creating a full-lenth column with only binned values
    input:
        - x -> single col nd-array
        - stride -> stride value
        - a_range -> min-max values (ndarray => shape(2,))
    '''
    a_min= a_range[0]
    a_max = a_range[1]
    start = cuda.grid(1)
    s = cuda.gridsize(1)
    # if a_max <= 1:
    #     balancer = 100
    for i in range(start, x.shape[0],s):
        if x[i]>= a_min and x[i]<=a_max:
            x[i] = np.int32((x[i] - a_min)/stride)
        else:
            x[i] = -1

def get_binwise_reduced_column(a_gpu, stride, a_range):
    '''
    description:
        calls the cuda jit function calc_binwise_reduced_column and resturns the result
    input:
        - a_gpu -> single col nd-array
        - stride -> stride value
        - a_range -> min-max values (ndarray => shape(2,))
    output:
        - a_gpu -> single col resulting nd-array
    '''
    calc_binwise_reduced_column[64,64](a_gpu,np.float64(stride),a_range)
    return a_gpu

def get_arrow_stream(record_batch):
    outputStream = io.BytesIO()
    writer = pa.ipc.RecordBatchStreamWriter(outputStream,record_batch.schema)
    writer.write_batch(record_batch)
    writer.close()
    return outputStream.getvalue()




def format_result(result_np:np.ndarray , return_format:str):
    '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
    '''
    pandas_df = pd.DataFrame(result_np,dtype=np.float64)
    
    if return_format == 'pandas':
        return pandas_df
    
    elif return_format == 'arrow':
        result_pa = pa.RecordBatch.from_pandas(pandas_df,preserve_index=True)
        return get_arrow_stream(result_pa)
    
    elif return_format == 'ColumnDataSource':
        pandas_df.columns = pandas_df.columns.astype(str)
        return ColumnDataSource(pandas_df)

def calc_data_tile_for_size(df, col_1, min_1, max_1, stride_1, cumsum:bool=True, return_format = 'pandas'):
    a1_range = cuda.to_device(np.asarray([min_1,max_1], dtype=np.float64))
    df.add_column(col_1+'_mod',get_binwise_reduced_column(df[col_1].copy().to_gpu_array(), stride_1, a1_range))
    groupby_result = df[[col_1+'_mod']].groupby(col_1+'_mod', method='hash',as_index=True).agg({col_1+'_mod':'count'})

    max_s = int((max_1-min_1)/stride_1)+1
    min_s = 1

    result = np.zeros(shape=(min_s,max_s)).astype(np.float64)[0]

    groupby_result_array_index = groupby_result.index.to_array().astype(int)
    groupby_result_array = groupby_result[groupby_result.columns[-1]].to_array()

    del(groupby_result)

    for index, value in np.ndenumerate(groupby_result_array_index):
        result[value] = groupby_result_array[index[0]]

    if cumsum:
        result_np = np.cumsum(result)
        
    else:
        result_np = result
    return format_result(result_np, return_format)
    # result_pa = pa.RecordBatch.from_pandas(pd.DataFrame(result_np,dtype=np.float64),preserve_index=True)
    # return get_arrow_stream(result_pa)

def calc_data_tile(df, active_view: Type[BaseChart], passive_view: Type[BaseChart], aggregate_fn:str='', cumsum:bool=True, return_format = 'pandas'):
    '''
    description:
        cuda jit function calculate the data tile with cumulative sums for a 2-col ndarray
    input:
        - df -> cudf dataframe
        - active_view -> chart class
        - passive_view -> chart class
        - aggregate_dict
        - cumsum: bool
        - return_format: pandas/arrow/bokeh.models.ColumnDataSource
    output:
        - pyarrow(2d-numpy array) -> data-tile data structure
    '''

    col_1, min_1, max_1, stride_1 = active_view.x, active_view.min_value, active_view.max_value, active_view.stride
    col_2, min_2, max_2, stride_2 = passive_view.x, passive_view.min_value, passive_view.max_value, passive_view.stride
    
    key = passive_view.y if passive_view.y is not None else passive_view.x
    if len(aggregate_fn) == 0:
        aggregate_fn = passive_view.aggregate_fn

    if aggregate_fn == 'mean':
        aggregate_dict = { key: ['sum', 'count']}
    else:
        aggregate_dict = { key: [aggregate_fn]}
    

    a1_range = cuda.to_device(np.asarray([min_1,max_1], dtype=np.float64))
    a2_range = cuda.to_device(np.asarray([min_2,max_2], dtype=np.float64))
    check_list = []
    if(key == col_1 and col_1+'_mod' not in df.columns):
        df.add_column(col_1+'_mod',get_binwise_reduced_column(df[col_1].copy().to_gpu_array(), stride_1, a1_range))
        check_list.append(col_1+'_mod')
    else:
        df[col_1] = get_binwise_reduced_column(df[col_1].copy().to_gpu_array(), stride_1, a1_range)
        check_list.append(col_1)
    if(key == col_2 and col_2+'_mod' not in df.columns):
        df.add_column(col_2+'_mod',get_binwise_reduced_column(df[col_2].copy().to_gpu_array(), stride_2, a2_range))
        check_list.append(col_2+'_mod')
    else:
        df[col_2] = get_binwise_reduced_column(df[col_2].copy().to_gpu_array(), stride_2, a2_range)
        check_list.append(col_2)

    # print(df[col_2+'_mod']).to_pandas()
    
    groupby_results = []
    for i in aggregate_dict[key]:
        agg = {key: i}
        groupby_results.append(df.groupby(check_list, method='hash',as_index=False).agg(agg))
    
    del(df)
    gc.collect()

    results = []
    for groupby_result in groupby_results:
        
        groupby_as_ndarray = cuda.to_device(groupby_result.to_pandas().values.astype(float))
        del(groupby_result)
        gc.collect()
        max_s = int((max_1-min_1)/stride_1) + 1
        min_s = int((max_2-min_2)/stride_2) + 1
        result = cuda.to_device(np.zeros(shape=(min_s,max_s)).astype(np.float64))

        # index_mins = cuda.to_device(np.asarray([min_1,min_2], dtype=np.float64))
        # index_strides = cuda.to_device(np.asarray([stride_1,stride_2], dtype=np.float64))

        calc_cumsum_data_tile[64,64](groupby_as_ndarray, result)
        if not cumsum:
            result_np = result.copy_to_host()
        else:
            result_np = np.cumsum(result.copy_to_host(),axis=1)

        results.append(format_result(result_np, return_format))
    
    if len(results) == 1:
        return results[0]
    return results