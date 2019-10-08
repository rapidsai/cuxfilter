import pandas as pd
import numpy as np
import xarray as xr
import cudatashader as ds
import cudatashader.transfer_functions as tf
from collections import OrderedDict

# Constants
np.random.seed(2)
n = 10000000                           # Number of points
cols = list('abcdefg')               # Column names of samples
start = 1456297053                   # Start time
end = start + 60 * 60 * 24           # End time   

# Generate a fake signal
time = np.linspace(start, end, n)
signal = np.random.normal(0, 0.3, size=n).cumsum() + 50

# Generate many noisy samples from the signal
noise = lambda var, bias, n: np.random.normal(bias, var, n)
data = {c: signal + noise(1, 10*(np.random.random() - 0.5), n) for c in cols}

# Add some "rogue lines" that differ from the rest 
cols += ['x'] ; data['x'] = signal + np.random.normal(0, 0.02, size=n).cumsum() # Gradually diverges
cols += ['y'] ; data['y'] = signal + noise(1, 20*(np.random.random() - 0.5), n) # Much noisier
cols += ['z'] ; data['z'] = signal # No noise at all

# Pick a few samples from the first line and really blow them out
locs = np.random.choice(n, 10)
data['a'][locs] *= 2

# Default plot ranges:
x_range = (start, end)
y_range = (1.2*signal.min(), 1.2*signal.max())

# print("x_range: {0} y_range: {0}".format(x_range,y_range))

# Create a dataframe
data['Time'] = np.linspace(start, end, n)
df = pd.DataFrame(data)
import cudf
cudf_df = cudf.DataFrame.from_pandas(df)

import cuXfilter
from cuXfilter.layouts import *

cux_df = cuXfilter.DataFrame.from_dataframe(cudf_df)

chart0 = cuXfilter.charts.cudatashader.stacked_lines(x='Time', y=['a', 'b', 'c', 'd', 'e', 'f', 'g', 'x', 'y', 'z'],
                                                    colors = ["red", "grey", "black", "purple", "pink",
                                                              "yellow", "brown", "green", "orange", "blue"]
                                                    )

chart4 = cuXfilter.charts.view_dataframe()

d = cux_df.dashboard([chart0, chart4])
d.show()