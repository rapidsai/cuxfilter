import panel as pn
import cudf
import pyarrow as pa
from typing import Type
from .dashboard import DashBoard
from .layouts import layout_1


def read_arrow(source):
    # print('reading arrow file as arrow table from disk')
    reader = pa.RecordBatchStreamReader(source)
    pa_df = reader.read_all()
    return pa_df

# class DataFrame:
class DataFrame:
    """
    A cuXfilter GPU DataFrame object
    """
    data: Type[cudf.DataFrame] = None

    @classmethod
    def from_arrow(cls, dataframe_location):
        """
        read an arrow file from disk as cuXfilter.DataFrame

        Parameters
        ----------
        dataframe_location: str or arrow in-memory table
        
        Returns
        -------
        cuXfilter.DataFrame object

        Examples
        --------

        Read dataframe as an arrow file from disk

        >>> import cuXfilter
        >>> cux_df = cuXfilter.DataFrame.from_arrow('./location/of/dataframe.arrow')

        """
        if type(dataframe_location) == str:
            df = cudf.DataFrame.from_arrow(read_arrow(dataframe_location))
        else:
            df = cudf.DataFrame.from_arrow(dataframe_location)
        return DataFrame(df)

    @classmethod
    def from_dataframe(cls, dataframe):
        """
        create a cuXfilter.DataFrame from cudf.DataFrame (zero-copy reference)

        Parameters
        ----------
        dataframe_location: cudf.DataFrame
        
        Returns
        -------
        cuXfilter.DataFrame object
        
        Examples
        --------
        
        Read dataframe from a cudf.DataFrame

        >>> import cuXfilter
        >>> import cudf
        >>> cudf_df = cudf.DataFrame({'key':[0,1,2,3,4], 'val':[float(i+10) for i in range(5)]})
        >>> cux_df = cuXfilter.DataFrame.from_dataframe(cudf_df)
            
        """
        return DataFrame(dataframe)
        
    def __init__(self, data):
        pn.extension()
        self.backup = data
        self.data = data.copy()

    def dashboard(self, charts:list, layout=layout_1, title='Dashboard', data_size_widget=True, warnings=False):
        """
        Creates a cuXfilter.DashBoard object
        
        Parameters
        ----------

        charts: list
            list of cuXfilter.charts
        
        layout: cuXfilter.layouts

        title: str
            title of the dashboard, default "Dashboard"

        data_size_widget: boolean
            flag to determine whether to diplay the current datapoints selected in the dashboard, default True

        warnings: boolean
            flag to disable or enable runtime warnings related to layouts, default False

        Examples
        --------
        >>> import cudf
        >>> import cuXfilter
        >>> from cuXfilter import charts
        >>> df = cudf.DataFrame({'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]})
        >>> cux_df = cuXfilter.DataFrame.from_dataframe(df)
        >>> line_chart_1 = charts.bokeh.line('key', 'val', data_points=5, add_interaction=False)
        
        >>> # create a dashboard object
        >>> d = cux_df.dashboard([line_chart_1])

        Returns
        -------
        cuXfilter.DashBoard object

        """
        return DashBoard(charts, self.data, layout, title, data_size_widget, warnings)
