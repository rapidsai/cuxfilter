import pandas as pd
import numpy as np
import cudf
import datetime

# Constants
np.random.seed(2)
# Number of points
n = 10000
# Column names of samples
cols = list("abcdefg")
# Start time
start = datetime.datetime(2010, 10, 1, 0)

# Generate a fake signal
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

data["Time"] = [start + datetime.timedelta(minutes=1) * i for i in range(n)]

# Create a dataframe
df = cudf.DataFrame.from_pandas(pd.DataFrame(data))
