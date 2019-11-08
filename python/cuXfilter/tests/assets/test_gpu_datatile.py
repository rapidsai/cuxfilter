import pytest

from cuXfilter.assets.numba_kernels.gpu_datatile import *
import numpy as np
from numba import cuda
import pandas as pd
import bokeh
from cuXfilter.charts.core.core_chart import BaseChart

def test_calc_cumsum_data_tile():
    df = cudf.DataFrame({
        'key': [float(i) for i in range(5)]*5,
        'val': [float(i*2) for i in range(5, 0, -1)]*5
        })
    max_s = int(df['key'].max() - df['key'].min()) + 1
    min_s = int(df['val'].max() - df['val'].min()) + 1
    df['val_mod'] = get_binwise_reduced_column(df['val'].copy().to_gpu_array(), 1, cuda.to_device(np.asarray([df['val'].min(),df['val'].max()])))
    groupby_as_ndarray = cuda.to_device(df.groupby(by=['key', 'val_mod'], method='hash',sort=False, as_index=False).agg({'val':'count'}).to_pandas().values.astype(float))

    result = cuda.to_device(np.zeros(shape=(min_s,max_s)).astype(np.float64))

    assert np.array_equal(groupby_as_ndarray.copy_to_host(), np.array([[2., 4., 5.],
       [1., 6., 5.],
       [0., 8., 5.],
       [3., 2., 5.],
       [4., 0., 5.]]))
    
    assert np.array_equal(result.copy_to_host(), np.array([[0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 0., 0.]]))

    calc_cumsum_data_tile[64,64](groupby_as_ndarray, result)

    assert np.array_equal(result.copy_to_host(),np.array([[0., 0., 0., 0., 5.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 5., 0.],
       [0., 0., 0., 0., 0.],
       [0., 0., 5., 0., 0.],
       [0., 0., 0., 0., 0.],
       [0., 5., 0., 0., 0.],
       [0., 0., 0., 0., 0.],
       [5., 0., 0., 0., 0.]]))

    result_np = np.cumsum(result.copy_to_host(),axis=1)

    assert np.array_equal(result_np, np.array([[0., 0., 0., 0., 5.],
       [0., 0., 0., 0., 0.],
       [0., 0., 0., 5., 5.],
       [0., 0., 0., 0., 0.],
       [0., 0., 5., 5., 5.],
       [0., 0., 0., 0., 0.],
       [0., 5., 5., 5., 5.],
       [0., 0., 0., 0., 0.],
       [5., 5., 5., 5., 5.]]))

@pytest.mark.parametrize( 'stride, test_arr, result', [
    (2, cuda.to_device(np.array([10.,  8.,  6.,  4.,  2., 10.,  8.,  6.,  4.,  2., 10.,  8.,  6.])),
    np.array([4., 3., 2., 1., 0., 4., 3., 2., 1., 0., 4., 3., 2.])),
    (1, cuda.to_device(np.array([10.,  8.,  6.,  4.,  2., 10.,  8.,  6.,  4.,  2., 10.,  8.,  6., 0.])),
    cuda.to_device(np.array([10.,  8.,  6.,  4.,  2., 10.,  8.,  6.,  4.,  2., 10.,  8.,  6., 0.])))
])
def test_calc_binwise_reduced_column(stride, test_arr, result):
    min, max = test_arr.copy_to_host().min(), test_arr.copy_to_host().max()
    test_res = get_binwise_reduced_column(test_arr, stride, cuda.to_device(np.asarray([min,max]))).copy_to_host()

    assert np.array_equal(test_res,result)

@pytest.mark.parametrize( 'result, return_format_str, return_format', [
    (np.array([[0., 0., 0., 0., 5.],[0., 0., 0., 0., 0.]]), 'pandas', pd.core.frame.DataFrame),
    (np.array([[0., 0., 0., 0., 5.],[0., 0., 0., 0., 0.]]), 'arrow', bytes),
    (np.array([[0., 0., 0., 0., 5.],[0., 0., 0., 0., 0.]]), 'ColumnDataSource', bokeh.models.sources.ColumnDataSource),
])
def test_format_result(result, return_format_str, return_format):
    assert type(format_result(result, return_format_str)) == return_format


def test_calc_data_tile_for_size():
    df = cudf.DataFrame({
                        'key': [float(i) for i in range(5)]*5,
                        'val': [float(i*2) for i in range(5, 0, -1)]*5
                        })
    col_1 = 'key'
    min_1, max_1 = df[col_1].min(), df[col_1].max()
    stride_1 = 1
    cumsum = True
    return_result = calc_data_tile_for_size(df=df, col_1=col_1, min_1=min_1, max_1=max_1, stride_1=stride_1, cumsum=cumsum)

    result = pd.DataFrame({0: {0: 5.0, 1: 10.0, 2: 15.0, 3: 20.0, 4: 25.0}})

    assert return_result.equals(result)

def test_calc_data_tile():
    df = cudf.DataFrame({
                        'key': [float(i) for i in range(5)]*5,
                        'val': [float(i*2) for i in range(5, 0, -1)]*5
                        })
    active_chart, passive_chart = BaseChart(), BaseChart()
    active_chart.x, active_chart.min_value = 'key', df['key'].min()
    active_chart.max_value, active_chart.stride = df['key'].max(), 1

    passive_chart.x, passive_chart.min_value = 'val', df['val'].min()
    passive_chart.max_value, passive_chart.stride = df['val'].max(), 1

    cumsum = True
    return_result = calc_data_tile(df=df, active_view=active_chart, passive_view=passive_chart, cumsum=cumsum)

    result = pd.DataFrame({0: {0: 0.0, 2: 0.0, 4: 0.0, 6: 0.0, 8: 5.0},
                        1: {0: 0.0, 2: 0.0, 4: 0.0, 6: 5.0, 8: 5.0},
                        2: {0: 0.0, 2: 0.0, 4: 5.0, 6: 5.0, 8: 5.0},
                        3: {0: 0.0, 2: 5.0, 4: 5.0, 6: 5.0, 8: 5.0},
                        4: {0: 5.0, 2: 5.0, 4: 5.0, 6: 5.0, 8: 5.0}})

    assert return_result.equals(result)


