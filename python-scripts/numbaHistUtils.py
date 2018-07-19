import numpy as np
from numba import cuda
import numba
from numba.pycc import CC

cc = CC('numbaHistUtils')

@cc.export('compute_bin','(f8,f8,f8,f8)')
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

if __name__ == "__main__":
    cc.compile()