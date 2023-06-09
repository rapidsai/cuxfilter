import panel as pn
import logging
import dask_cudf
from panel.config import panel_extension
from ...layouts import chart_view

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
