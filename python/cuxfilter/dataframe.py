import cudf
import pyarrow as pa
from typing import Type

from .dashboard import DashBoard
from .layouts import single_feature
from .themes import light
from .assets import notebook_assets


def read_arrow(source):
    # print('reading arrow file as arrow table from disk')
    reader = pa.RecordBatchStreamReader(source)
    pa_df = reader.read_all()
    return pa_df


# class DataFrame:
class DataFrame:
    """
    A cuxfilter GPU DataFrame object
    """

    data: Type[cudf.DataFrame] = None
    is_graph = False
    edges: Type[cudf.DataFrame] = None

    @classmethod
    def from_arrow(cls, dataframe_location):
        """
        read an arrow file from disk as cuxfilter.DataFrame

        Parameters
        ----------
        dataframe_location: str or arrow in-memory table

        Returns
        -------
        cuxfilter.DataFrame object

        Examples
        --------

        Read dataframe as an arrow file from disk

        >>> import cuxfilter
        >>> cux_df = cuxfilter.DataFrame.from_arrow(
            './location/of/dataframe.arrow'
            )

        """
        if isinstance(dataframe_location, str):
            df = cudf.DataFrame.from_arrow(read_arrow(dataframe_location))
        else:
            df = cudf.DataFrame.from_arrow(dataframe_location)
        return cls(df)

    @classmethod
    def from_dataframe(cls, dataframe):
        """
        create a cuxfilter.DataFrame from cudf.DataFrame/dask_cudf.DataFrame
        (zero-copy reference)

        Parameters
        ----------
        dataframe_location: cudf.DataFrame or dask_cudf.DataFrame

        Returns
        -------
        cuxfilter.DataFrame object

        Examples
        --------

        Read dataframe from a cudf.DataFrame/dask_cudf.DataFrame

        >>> import cuxfilter
        >>> import cudf
        >>> cudf_df = cudf.DataFrame(
        >>>     {
        >>>         'key': [0, 1, 2, 3, 4],
        >>>         'val':[float(i + 10) for i in range(5)]
        >>>     }
        >>> )
        >>> cux_df = cuxfilter.DataFrame.from_dataframe(cudf_df)

        """
        return cls(dataframe)

    @classmethod
    def load_graph(cls, graph):
        """
        create a cuxfilter.DataFrame from cudf.DataFrame/dask_cudf.DataFrame
        (zero-copy reference) from a graph object

        Parameters
        ----------
        tuple object (nodes, edges) where nodes and edges are cudf DataFrames

        Returns
        -------
        cuxfilter.DataFrame object

        Examples
        --------

        load graph from cugraph object

        >>> import cuxfilter
        >>> import cudf, cugraph
        >>> edges = cudf.DataFrame(
        >>>     {
        >>>         'source': [0, 1, 2, 3, 4],
        >>>         'target':[0,1,2,3,4],
        >>>         'weight':[4,4,2,6,7],
        >>>     }
        >>> )
        >>> G = cugraph.Graph()
        >>> G.from_cudf_edgelist(edges)
        >>> cux_df = cuxfilter.DataFrame.load_graph((G.nodes(), G.edges()))

        load graph from (nodes, edges)

        >>> import cuxfilter
        >>> import cudf
        >>> nodes = cudf.DataFrame(
        >>>     {
        >>>         'vertex': [0, 1, 2, 3, 4],
        >>>         'x':[0,1,2,3,4],
        >>>         'y':[4,4,2,6,7],
        >>>         'attr': [0,1,1,1,1]
        >>>     }
        >>> )
        >>> edges = cudf.DataFrame(
        >>>     {
        >>>         'source': [0, 1, 2, 3, 4],
        >>>         'target':[0,1,2,3,4],
        >>>         'weight':[4,4,2,6,7],
        >>>     }
        >>> )
        >>> cux_df = cuxfilter.DataFrame.load_graph((nodes,edges))

        """
        if isinstance(graph, tuple):
            nodes, edges = graph
            df = cls(nodes)
            df.is_graph = True
            df.edges = edges
            return df
        raise ValueError(
            "Expected value for graph - (nodes[cuDF], edges[cuDF])"
        )

    def __init__(self, data):
        self.data = data

    def dashboard(
        self,
        charts: list,
        layout=single_feature,
        theme=light,
        title="Dashboard",
        data_size_widget=True,
        warnings=False,
        layout_array=None
    ):
        """
        Creates a cuxfilter.DashBoard object

        Parameters
        ----------

        charts: list
            list of cuxfilter.charts

        layout: cuxfilter.layouts

        title: str
            title of the dashboard, default "Dashboard"

        data_size_widget: boolean
            flag to determine whether to diplay the current datapoints
            selected in the dashboard, default True

        warnings: boolean
            flag to disable or enable runtime warnings related to layouts,
            default False

        Examples
        --------
        >>> import cudf
        >>> import cuxfilter
        >>> from cuxfilter.charts import bokeh
        >>> df = cudf.DataFrame(
        >>>     {
        >>>         'key': [0, 1, 2, 3, 4],
        >>>         'val':[float(i + 10) for i in range(5)]
        >>>     }
        >>> )
        >>> cux_df = cuxfilter.DataFrame.from_dataframe(df)
        >>> line_chart_1 = bokeh.line(
        >>>     'key', 'val', data_points=5, add_interaction=False
        >>> )

        >>> # create a dashboard object
        >>> d = cux_df.dashboard([line_chart_1])

        Returns
        -------
        cuxfilter.DashBoard object

        """
        if notebook_assets.pn.config.js_files == {}:
            notebook_assets.load_notebook_assets()

        return DashBoard(
            charts, self, layout, theme, title, data_size_widget, warnings,
            layout_array
        )
