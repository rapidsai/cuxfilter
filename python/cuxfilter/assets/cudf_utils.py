import dask_cudf
import dask.dataframe as dd
from ..charts.constants import CUDF_DATETIME_TYPES


def get_min_max(df, col_name):
    min, max = df[col_name].min(), df[col_name].max()
    if isinstance(df, dask_cudf.DataFrame):
        if df[col_name].dtype in CUDF_DATETIME_TYPES:
            return datetime_dask_fix(*dd.compute(min, max))
        return dd.compute(min, max)

    return (min, max)


def datetime_dask_fix(min, max):
    """
    dask_cudf returns a datetime.timestamp object for
    dask_cudf.series -> min, max compute operations,
    whereas cudf equivalent returns a numpy.datetime64[ns] objects.

    This function converts the timestamps to numpy.datetime64 objects for
    consistency.
    """
    return (min.to_datetime64(), max.to_datetime64())


def cull_empty_partitions(df):
    ll = list(df.map_partitions(len).compute())
    df_delayed = df.to_delayed()
    df_delayed_new = list()
    pempty = None
    for ix, n in enumerate(ll):
        if 0 == n:
            pempty = df.get_partition(ix)
        else:
            df_delayed_new.append(df_delayed[ix])
    if pempty is not None:
        df = dd.from_delayed(df_delayed_new, meta=pempty)
    return df


def query_df(df, query, local_dict, indices=None):
    # filter the source data with current queries: indices and query strs
    result = df if indices is None else df[indices]

    if len(query) > 0:
        result = result.query(expr=query, local_dict=local_dict)

    # cull any empty partitions, since dask_cudf dataframe filtering
    # may result in one
    if isinstance(df, dask_cudf.DataFrame):
        result = cull_empty_partitions(result)

    return result
