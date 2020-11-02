import dask_cudf


def get_min_max(df, col_name):
    min, max = df[col_name].min(), df[col_name].max()
    if isinstance(df, dask_cudf.core.DataFrame):
        return (min.compute(), max.compute())

    return (min, max)
