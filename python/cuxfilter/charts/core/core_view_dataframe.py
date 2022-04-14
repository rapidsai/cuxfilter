import panel as pn
import logging
from panel.config import panel_extension
import dask_cudf

from .core_chart import BaseChart
from ...layouts import chart_view
from ...assets import cudf_utils

css = """
.dataframe table{
  border: none;
}

.panel-df table{
    width: 100%;
    border-collapse: collapse;
    border: none;
}
.panel-df td{
    white-space: nowrap;
    overflow: auto;
    text-overflow: ellipsis;
}
"""

pn.config.raw_css += [css]


class ViewDataFrame:
    _height: int = 0
    columns = None
    _width: int = 0
    chart = None
    source = None
    use_data_tiles = False
    drop_duplicates = False
    _initialized = False
    # widget=False can only be rendered the main layout
    is_widget = False

    def __init__(
        self,
        columns=None,
        drop_duplicates=False,
        width=400,
        height=400,
        force_computation=False,
    ):
        self.columns = columns
        self._width = width
        self._height = height
        self.drop_duplicates = drop_duplicates
        self.force_computation = force_computation

    @property
    def name(self):
        return self.chart_type

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        if self.chart is not None:
            self.update_dimensions(width=value)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        if self.chart is not None:
            self.update_dimensions(height=value)

    def initiate_chart(self, dashboard_cls):
        data = dashboard_cls._cuxfilter_df.data
        if isinstance(data, dask_cudf.core.DataFrame):
            if self.force_computation:
                self.generate_chart(data.compute())
            else:
                print(
                    "displaying only 1st partitions top 1000 rows for ",
                    "view_dataframe - dask_cudf to avoid partition based ",
                    "computation use force_computation=True for viewing ",
                    "top-level view of entire DataFrame. ",
                    "Warning - would slow the dashboard down significantly",
                )
                self.generate_chart(
                    data.head(
                        1000,
                        npartitions=data.npartitions,
                        compute=True,
                    )
                )
        else:
            self.generate_chart(data)

    def _format_data(self, data):
        if self.drop_duplicates:
            return data.drop_duplicates()
        return data

    def generate_chart(self, data):
        if self.columns is None:
            self.columns = list(data.columns)
        style = {
            "width": "100%",
            "height": "100%",
            "overflow-y": "auto",
            "font-size": "0.5vw",
            "overflow-x": "auto",
        }
        self.chart = pn.pane.HTML(
            self._format_data(data[self.columns]),
            style=style,
            css_classes=["panel-df"],
        )

    def _repr_mimebundle_(self, include=None, exclude=None):
        view = self.view()
        if self._initialized and panel_extension._loaded:
            return view._repr_mimebundle_(include, exclude)

        if self._initialized is False:
            logging.warning(
                "dashboard has not been initialized."
                "Please run cuxfilter.dashboard.Dashboard([...charts])"
                " to view this object in notebook"
            )

        if panel_extension._loaded is False:
            logging.warning(
                "notebooks assets not loaded."
                "Please run cuxfilter.load_notebooks_assets()"
                " to view this object in notebook"
            )
            if isinstance(view, pn.Column):
                return view.pprint()
        return None

    def view(self):
        return chart_view(self.chart, width=self.width, title="Dataset View")

    def reload_chart(self, data, patch_update: bool):
        if isinstance(data, dask_cudf.core.DataFrame):
            if self.force_computation:
                self.chart[0].object = self._format_data(
                    data[self.columns].compute()
                )
            else:
                self.chart[0].object = self._format_data(
                    data[self.columns].head(
                        1000, npartitions=data.npartitions, compute=True
                    )
                )
        else:
            self.chart[0].object = self._format_data(data[self.columns])

    def update_dimensions(self, width=None, height=None):
        """
        Parameters
        ----------

        Ouput
        -----
        """
        if width is not None:
            self.chart.width = width
        if height is not None:
            self.chart.height = height

    def _compute_source(self, data, query, local_dict, indices):
        """
        Compute source dataframe based on the values query and indices.
        If both are not provided, return the original dataframe.
        """
        return cudf_utils.query_df(data, query, local_dict, indices)

    def query_chart_by_range(
        self,
        active_chart: BaseChart,
        query_tuple,
        data,
        query="",
        local_dict={},
        indices=None,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: None in case of Gpu Geo Scatter charts
        -------------------------------------------

        Ouput:
        """
        min_val, max_val = query_tuple
        final_query = (
            str(min_val) + "<=" + active_chart.x + "<=" + str(max_val)
        )
        if len(query) > 0:
            final_query += " and " + query
        self.reload_chart(
            self._compute_source(data, final_query, local_dict, indices),
            False,
        )

    def query_chart_by_indices(
        self,
        active_chart: BaseChart,
        old_indices,
        new_indices,
        data,
        query="",
        local_dict={},
        indices=None,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: None in case of Gpu Geo Scatter charts
        -------------------------------------------

        Ouput:
        """
        if "" in new_indices:
            new_indices.remove("")
        if len(new_indices) == 0:
            # case: all selected indices were reset
            # reset the chart
            final_query = query
        elif len(new_indices) == 1:
            final_query = active_chart.x + "==" + str(float(new_indices[0]))
            if len(query) > 0:
                final_query += " and " + query
        else:
            new_indices_str = ",".join(map(str, new_indices))
            final_query = active_chart.x + " in (" + new_indices_str + ")"
            if len(query) > 0:
                final_query += " and " + query

        self.reload_chart(
            self._compute_source(data, final_query, local_dict, indices),
            False,
        )
