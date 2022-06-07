import cudf
import dask_cudf


def initialize_df(type, *df_args):
    df = cudf.DataFrame(*df_args)
    if type == cudf.DataFrame:
        return df
    return dask_cudf.from_cudf(df, npartitions=2)


def df_equals(df1, df2):
    df1 = df1.compute() if isinstance(df1, dask_cudf.DataFrame) else df1
    df2 = df2.compute() if isinstance(df2, dask_cudf.DataFrame) else df2

    return df1.equals(df2)


df_types = [cudf.DataFrame, dask_cudf.DataFrame]
