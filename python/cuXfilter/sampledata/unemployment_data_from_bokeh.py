import cudf
import pandas as pd
from bokeh.sampledata.unemployment1948 import data

data["Year"] = data["Year"].astype(str)
data = data.set_index("Year")
data.drop("Annual", axis=1, inplace=True)
data.columns.name = "Month"

years = list(data.index)
months = list(data.columns)

# reshape to 1D array or rates with a month and year for each row.
df = pd.DataFrame(data.stack(), columns=["rate"]).reset_index()

df["Month"] = pd.to_datetime(df.Month, format="%b").dt.month
df["Year"] = df["Year"].astype("float64")
df["Month"] = df["Month"].astype("float64")


df = cudf.DataFrame.from_pandas(df)
