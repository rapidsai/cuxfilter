import numpy as np
from numba import cuda
import cudf
import numba
import pyarrow as pa
import pandas as pd
import io
import gc
from typing import Type

from ...charts.core.core_chart import BaseChart

@numba.jit(nopython=True,parallel=True)
def compute_bin(x, n, xmin, xmax):
    '''
    description:
        compute actual bin number
    input:
        - x: ndarray
        - n: number of bins
        - xmin: min value in x ndarray
        - xmax: max value in x ndarray
    '''
    # special case to mirror NumPy behavior for last bin
    if x == xmax:
        return n - 1 # a_max always in last bin

    # SPEEDTIP: Remove the float64 casts if you don't need to exactly reproduce NumPy
    bin = np.int32(n * (np.float64(x) - np.float64(xmin)) / (np.float64(xmax) - np.float64(xmin)))

    if bin < 0 or bin >= n:
        return None
    else:
        return bin

@cuda.jit
def min_max(x, min_max_array):
    '''
    description:
        cuda jit to calculate the min and max values for the ndarray
    input:
        - x: ndarray
        - min_max_array: cuda.to_device(np.array([dtype_max, dtype_min], dtype=np.float32))
    '''
    nelements = x.shape[0]

    start = cuda.grid(1)
    stride = cuda.gridsize(1)

    # Array already seeded with starting values appropriate for x's dtype
    # Not a problem if this array has already been updated
    local_min = min_max_array[0]
    local_max = min_max_array[1]

    for i in range(start, x.shape[0], stride):
        element = x[i]
        local_min = min(element, local_min)
        local_max = max(element, local_max)

    # Now combine each thread local min and max
    cuda.atomic.min(min_max_array, 0, local_min)
    cuda.atomic.max(min_max_array, 1, local_max)

@cuda.jit
def histogram(x, x_range, histogram_out):
    '''
    description:
        calculate histogram using cuda.jit
    input:
        x -> ndarray(1-col)
        x_range -> (min,max)
        histogram_out -> cuda.to_device array(np.zeros) that will store the frequencies
    '''
    nbins = histogram_out.shape[0]
    xmin, xmax = x_range
    bin_width = (xmax - xmin) / nbins
    start = cuda.grid(1)
    stride = cuda.gridsize(1)
    for i in range(start, x.shape[0], stride):
        # note that calling a numba.jit function from CUDA automatically
        # compiles an equivalent CUDA device function!
        bin_number = compute_bin(x[i], nbins, xmin, xmax)
        # counter[0] = counter[0] + 1
        if bin_number >= 0 and bin_number < histogram_out.shape[0]:
            cuda.atomic.add(histogram_out, bin_number, 1)


def dtype_min_max(dtype):
    '''
       description:
           Get the min and max value for a numeric dtype
       input:
           dtype
    '''
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
    else:
        info = np.finfo(dtype)
    return info.min, info.max

@cuda.jit
def get_bin_edges(a_range, bin_edges):
    '''
    description:
        cuda jit function calculate the bin edge values
    input:
        - a_range: ndarray containin min and max values of the array
        - bin_edges: result ndarray of shape (binsize,)

    '''
    a_min,a_max = a_range
    nbins = bin_edges.shape[0]
    delta = (a_max - a_min) / nbins
    for i in range(bin_edges.shape[0]):
        bin_edges[i] = a_min + i * delta

    bin_edges[-1] = a_max  # Avoid roundoff error on last point

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
    _balancer = 1
    if a_max <= 1:
        _balancer = 100
    start = cuda.grid(1)
    s = cuda.gridsize(1)
    for i in range(start, x.shape[0],s):
        if x[i]>= a_min and x[i]<=a_max:
            x[i] = stride*np.int32((x[i])/stride)/_balancer
        else:
            x[i] = -1/_balancer

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
    calc_binwise_reduced_column[64,64](a_gpu,np.float32(stride),a_range)
    return a_gpu

def calc_value_counts(a_gpu, bins):
    '''
    description:
        main function to calculate histograms
    input:
        - a_gpu: gpu array(cuda ndarray) -> 1-column only
        - bins: number of bins
    output:
        frequencies(ndarray), bin_edge_values(ndarray)
    '''
    ### Find min and max value in array
    dtype_min, dtype_max = dtype_min_max(a_gpu.dtype)
    # Put them in the array in reverse order so that they will be replaced by the first element in the array
    min_max_array_gpu = cuda.to_device(np.array([dtype_max, dtype_min], dtype=np.float32))
    # min_max[64, 64](a_gpu,index_gpu, min_max_array_gpu)
    min_max[64, 64](a_gpu, min_max_array_gpu)
    bin_edges = cuda.to_device(np.zeros(shape=(bins,), dtype=np.float64))

    get_bin_edges[64,64](min_max_array_gpu,bin_edges)

    ### Bin the data into a histogram
    histogram_out = cuda.to_device(np.zeros(shape=(bins,), dtype=np.int32))
    histogram[64, 64](a_gpu, min_max_array_gpu, histogram_out)
    return bin_edges.copy_to_host(), histogram_out.copy_to_host()

def calc_groupby(chart: Type[BaseChart], data):
    '''
    description:
        main function to calculate histograms
    input:
        - chart
        - data
    output:
        frequencies(ndarray), bin_edge_values(ndarray)
    '''

    y_min, y_max = data[chart.y].min(), data[chart.y].max()
    a_x_range = cuda.to_device(np.asarray([chart.min_value, chart.max_value], dtype=np.float32))
    a_y_range = cuda.to_device(np.asarray([y_min, y_max], dtype=np.float32))

    if y_max < 1:
        stride_y = (data[chart.y].max() - data[chart.y].min())/chart.data_points
    else:
        stride_y = chart.stride_type((data[chart.y].max() - data[chart.y].min())/chart.data_points)

    temp_df = cudf.DataFrame()
    temp_df.add_column(chart.x, get_binwise_reduced_column(data[chart.x].copy().to_gpu_array(), chart.stride, a_x_range))
    temp_df.add_column(chart.y, data[chart.y].copy().to_gpu_array())
    
    
    groupby_res = temp_df.groupby(by=[chart.x], as_index=False).agg({chart.y:chart.aggregate_fn}).to_pandas()

    del(temp_df)
    gc.collect()

    return groupby_res.to_numpy().transpose()

def aggregated_column_unique(chart: Type[BaseChart], data):
    '''
    description:
        main function to calculate histograms
    input:
        - chart
        - data
    output:
        list_of_unique_values
    '''

    a_range = cuda.to_device(np.array([chart.min_value, chart.max_value]))
    temp_df = cudf.DataFrame()
    temp_df.add_column(chart.x, get_binwise_reduced_column(data[chart.x].copy().to_gpu_array(), chart.stride, a_range))
    return temp_df[chart.x].unique().to_pandas().tolist()