# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import panel as pn
import holoviews as hv
import logging
import dask_cudf
from panel.config import panel_extension

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
    columns = None
    chart = None
    source = None
    use_data_tiles = False
    drop_duplicates = False
    _initialized = False
    # widget=False can only be rendered the main layout
    is_widget = False
    title = "Dataset View"

    def __init__(
        self,
        columns=None,
        drop_duplicates=False,
        force_computation=False,
    ):
        self.columns = columns
        self.drop_duplicates = drop_duplicates
        self.force_computation = force_computation

    @property
    def name(self):
        return f"{self.chart_type}_{self.columns}"

    def initiate_chart(self, dashboard_cls):
        data = dashboard_cls._cuxfilter_df.data
        if isinstance(data, dask_cudf.DataFrame):
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
        if not self.force_computation:
            data = data.head(1000)
        if self.drop_duplicates:
            data = data.drop_duplicates()
        return data

    def generate_chart(self, data):
        if self.columns is None:
            self.columns = list(data.columns)
        self.chart = hv.Table(self._format_data(data[self.columns]))

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

    def view(self, width=600, height=400):
        return pn.panel(self.chart, width=width, height=height)

    def get_dashboard_view(self):
        return pn.panel(self.chart, sizing_mode="stretch_both")

    def reload_chart(self, data):
        if isinstance(data, dask_cudf.DataFrame):
            if self.force_computation:
                self.chart.data = self._format_data(
                    data[self.columns].compute()
                )
            else:
                self.chart.data = self._format_data(
                    data[self.columns].head(
                        1000, npartitions=data.npartitions, compute=True
                    )
                )
        else:
            self.chart.data = self._format_data(data[self.columns])
