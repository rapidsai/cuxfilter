import numpy as np
from numba import cuda
import numba

@numba.jit(nopython=True,parallel=True)
def compute_bin(x, n, xmin, xmax):
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
def histogram(x, x_range, histogram_out):
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

@cuda.jit
def min_max(x, min_max_array):
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


def dtype_min_max(dtype):
    '''Get the min and max value for a numeric dtype'''
    if np.issubdtype(dtype, np.integer):
        info = np.iinfo(dtype)
    else:
        info = np.finfo(dtype)
    return info.min, info.max


@cuda.jit
def get_bin_edges(a_range, bin_edges):
    a_min,a_max = a_range
    nbins = bin_edges
    delta = (a_max - a_min) / bin_edges.shape[0]
    for i in range(bin_edges.shape[0]):
        bin_edges[i] = a_min + i * delta

    bin_edges[-1] = a_max  # Avoid roundoff error on last point


def numba_gpu_histogram(a_gpu, bins):
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
    return histogram_out.copy_to_host(), bin_edges.copy_to_host()
