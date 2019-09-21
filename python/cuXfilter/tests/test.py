import cudf
import cuXfilter
from cuXfilter import charts

n=5
df = cudf.DataFrame({'key': [i for i in range(n)],'key2':[i for i in range(n)], 'val':[float(i + 10) for i in range(n)], 'val2': [float(i*10) for i in range(1, n+1)]})
cux_df = cuXfilter.DataFrame.from_dataframe(df)

