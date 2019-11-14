import pandas as pd
import numpy as np
import cudf

# Constants
np.random.seed(2)
# Number of points
n = 10000000
# Column names of samples
cols = list("abcdefg")
# Start time
start = 1456297053
# End time
end = start + 60 * 60 * 24

# Generate a fake signal
time = np.linspace(start, end, n)
signal = np.random.normal(0, 0.3, size=n).cumsum() + 50


# Generate many noisy samples from the signal
def noise(var, bias, n):
    return np.random.normal(bias, var, n)


data = {c: signal + noise(1, 10 * (np.random.random() - 0.5), n) for c in cols}

# Add some "rogue lines" that differ from the rest
# Gradually diverges
cols += ["x"]
data["x"] = signal + np.random.normal(0, 0.02, size=n).cumsum()
# Much noisier
cols += ["y"]
data["y"] = signal + noise(1, 20 * (np.random.random() - 0.5), n)
# No noise at all
cols += ["z"]
data["z"] = signal

# Pick a few samples from the first line and really blow them out
locs = np.random.choice(n, 10)
data["a"][locs] *= 2

# Default plot ranges:
x_range = (start, end)
y_range = (1.2 * signal.min(), 1.2 * signal.max())
# Create a dataframe
data["Time"] = np.linspace(start, end, n)
df = cudf.DataFrame.from_pandas(pd.DataFrame(data))
