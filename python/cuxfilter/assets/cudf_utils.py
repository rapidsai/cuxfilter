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

    This function converts the timestamps to numpy.datetime64 objects for consistency
    """
    return (min.to_datetime64(), max.to_datetime64())
