import pandas as pd
import numpy as np
import xarray as xr
from collections import OrderedDict

import cudf

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
# Create a dataframe
data['Time'] = np.linspace(start, end, n)
df = cudf.DataFrame.from_pandas(pd.DataFrame(data))