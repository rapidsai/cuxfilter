# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict, Union
import bokeh.embed.util as u
import cudf
import dask_cudf
import panel as pn
from panel.io.server import get_server
from bokeh.embed import server_document
import os
import urllib
import warnings
from collections import Counter

from cuxfilter.charts.core import BaseChart, BaseWidget, ViewDataFrame
from cuxfilter.layouts import single_feature
from cuxfilter.charts.panel_widgets import data_size_indicator
from cuxfilter.assets import get_open_port, cudf_utils
from cuxfilter.themes import default

DEFAULT_NOTEBOOK_URL = "http://localhost:8888"


def _get_host(url):
    parsed_url = urllib.parse.urlparse(url)
    if parsed_url.scheme not in ["http", "https"]:
        raise ValueError("url should contain protocol(http or https)")
    return parsed_url


def _create_dashboard_url(notebook_url: str, port: int, service_proxy=None):
    service_url_path = ""
    notebook_url = f"{notebook_url.scheme}://{notebook_url.netloc}"

    if service_proxy == "jupyterhub":
        if "JUPYTERHUB_SERVICE_PREFIX" not in os.environ:
            raise EnvironmentError(
                "JUPYTERHUB_SERVICE_PREFIX environment variable "
                + "not set, service_proxy=jupyterhub will only work "
                + "in a jupyterhub environment"
            )
        service_url_path = os.environ["JUPYTERHUB_SERVICE_PREFIX"]

    proxy_url_path = "proxy/%d/" % port

    user_url = urllib.parse.urljoin(notebook_url, service_url_path)
    full_url = urllib.parse.urljoin(user_url, proxy_url_path)
    return full_url


class DuplicateChartsWarning(Warning): ...


def _check_if_duplicates(charts):
    _charts = [i.name for i in charts]
    dups = [k for k, v in Counter(_charts).items() if v > 1]
    if len(dups) > 0:
        warnings.warn(
            (
                f"{dups} \n Only unique chart names "
                "are supported, please provide a unique title parameter to "
                "each chart"
            ),
            DuplicateChartsWarning,
        )


class DashBoard:
    """
    A cuxfilter GPU DashBoard object.
    Examples
    --------

    Create a dashboard

    >>> import cudf
    >>> import cuxfilter
    >>> from cuxfilter.charts import bokeh, panel_widgets
    >>> df = cudf.DataFrame(
    >>>     {'key': [0, 1, 2, 3, 4], 'val':[float(i + 10) for i in range(5)]}
    >>> )
    >>> cux_df = cuxfilter.DataFrame.from_dataframe(df)
    >>> line_chart_1 = bokeh.line(
    >>>     'key', 'val', data_points=5, add_interaction=False
    >>> )
    >>> line_chart_2 = bokeh.bar(
    >>>     'val', 'key', data_points=5, add_interaction=False
    >>> )
    >>> sidebar_widget = panel_widgets.card("test")
    >>> d = cux_df.dashboard(charts=[line_chart_1, line_chart_2],
    >>> sidebar=[sidebar_widget])
    >>> d
    `cuxfilter DashBoard
    [title] Markdown(str)
    [chart0] Markdown(str, sizing_mode='stretch_both'), ['nav'])
    [chart1] Column(sizing_mode='scale_both', width=1600)
        [0] Bokeh(Figure)
    [chart2] Column(sizing_mode='scale_both', width=1600)
        [0] Bokeh(Figure)`
    >>> # d.app() for serving within notebook cell,
    >>> # d.show() for serving as a separate web-app
    >>> d.app() #or d.show()
    displays interactive dashboard

    do some visual querying/ crossfiltering
    """

    _charts: Dict[str, Union[BaseChart, BaseWidget, ViewDataFrame]]
    _query_str_dict: Dict[str, str]
    _query_local_variables_dict = {}
    _dashboard = None
    _theme = None
    _notebook_url = DEFAULT_NOTEBOOK_URL
    _current_server_type = "show"
    _layout_array = None
    server = None

    @property
    def queried_indices(self):
        """
        Read-only propery queried_indices returns a merged index
        of all queried index columns present in self._query_str_dict
        as a `cudf.Series` or `dask_cudf.Series`.

        Returns None if no index columns are present.

        :meta private:
        """
        result = None
        df_module = (
            cudf
            if isinstance(self._cuxfilter_df.data, cudf.DataFrame)
            else dask_cudf
        )
        selected_indices = {
            key: value.reset_index(drop=True)
            for (key, value) in self._query_str_dict.items()
            if type(value)
            in [
                cudf.DataFrame,
                dask_cudf.DataFrame,
                cudf.Series,
                dask_cudf.Series,
            ]
        }
        if len(selected_indices) > 0:
            result = (
                df_module.concat(list(selected_indices.values()), axis=1)
                .set_index(self._cuxfilter_df.data.index)
                .fillna(False)
                .all(axis=1)
            )

        return result

    def __init__(
        self,
        charts=[],
        sidebar=[],
        dataframe=None,
        layout=single_feature,
        theme=default,
        title="Dashboard",
        data_size_widget=True,
        show_warnings=False,
        layout_array=None,
    ):
        self._cuxfilter_df = dataframe
        self._charts = dict()
        self._sidebar = dict()
        self._query_str_dict = dict()

        # check if charts and sidebar lists contain cuxfilter.charts with
        # duplicate names
        _check_if_duplicates(charts)
        _check_if_duplicates(sidebar)

        # widgets can be places both in sidebar area AND chart area
        # but charts cannot be placed in the sidebar area due to size
        # and resolution constraints
        # process all main dashboard charts
        for chart in charts:
            chart.initiate_chart(self)
            chart._initialized = True
            self._charts[chart.name] = chart

        # add data_size_indicator to sidebar if data_size_widget=True
        if data_size_widget:
            sidebar.insert(0, data_size_indicator(title_size="14pt"))

        # process all sidebar widgets
        for chart in sidebar:
            if chart.is_widget:
                chart.initiate_chart(self)
                chart._initialized = True
                self._sidebar[chart.name] = chart

        self.title = title
        self._dashboard = layout()
        self._theme = theme
        self._layout_array = layout_array
        # handle dashboard warnings
        if not show_warnings:
            u.log.disabled = True
            warnings.filterwarnings("ignore")
        else:
            u.log.disabled = False
            warnings.filterwarnings("default")

    @property
    def charts(self):
        """
        Charts in the dashboard as a dictionary.
        """
        return {**self._charts, **self._sidebar}

    def add_charts(self, charts=[], sidebar=[]):
        """
        Adding more charts to the dashboard, after it has been initialized.

        Parameters
        ----------
        charts: list
            list of cuxfilter.charts objects

        sidebar: list
            list of cuxfilter.charts.panel_widget objects

        Notes
        -----
        After adding the charts, refresh the dashboard app
        tab to see the updated charts. Charts of type widget cannot be added
        to sidebar but widgets can be added to charts(main layout)

        Examples
        --------

        >>> import cudf
        >>> import cuxfilter
        >>> from cuxfilter.charts import bokeh, panel_widgets
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
        >>> d = cux_df.dashboard([line_chart_1])
        >>> line_chart_2 = bokeh.bar(
        >>>     'val', 'key', data_points=5, add_interaction=False
        >>> )
        >>> d.add_charts(charts=[line_chart_2])
        >>> # or
        >>> d.add_charts(charts=[], sidebar=[panel_widgets.card("test")])

        """
        if len(charts) > 0 or len(sidebar) > 0:
            for chart in charts:
                if chart not in self._charts:
                    self._charts[chart.name] = chart
            for chart in sidebar:
                if chart not in self._sidebar and chart.is_widget:
                    self._sidebar[chart.name] = chart
            self._reinit_all_charts()
            self._restart_current_server()

    def _restart_current_server(self):
        if self.server is not None:
            self.stop()
            getattr(self, self._current_server_type)(
                notebook_url=self._notebook_url, port=self.server.port
            )

    def _reinit_all_charts(self):
        self._query_str_dict = dict()

        for chart in self.charts.values():
            chart.initiate_chart(self)
            chart._initialized = True

    def _query(self, query_str):
        """
        Query the cudf.DataFrame
        """
        # filter the source data with current queries: indices and query strs
        return cudf_utils.query_df(
            self._cuxfilter_df.data,
            query_str,
            self._query_local_variables_dict,
            self.queried_indices,
        )

    def _generate_query_str(self, query_dict=None, ignore_chart=""):
        """
        Generate query string based on current crossfiltered state of
        the dashboard.
        """
        popped_value = None
        query_dict = query_dict or self._query_str_dict
        if (
            isinstance(ignore_chart, (BaseChart, BaseWidget, ViewDataFrame))
            and len(ignore_chart.name) > 0
            and ignore_chart.name in query_dict
        ):
            popped_value = query_dict.pop(ignore_chart.name, None)

        # extract string queries from query_dict,
        # as self.query_dict also contains cudf.Series indices
        str_queries_list = [x for x in query_dict.values() if type(x) is str]
        return_query_str = " and ".join(str_queries_list)

        # adding the popped value to the query_str_dict again
        if popped_value is not None:
            query_dict[ignore_chart.name] = popped_value

        return return_query_str

    def export(self):
        """
        Export the cudf.DataFrame based on the current filtered state of
        the dashboard.

        Also prints the query string of the current state of the dashboard.

        Returns
        -------
        cudf.DataFrame based on the current filtered state of the dashboard.

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
        >>> line_chart_2 = bokeh.bar(
        >>>     'val', 'key', data_points=5, add_interaction=False
        >>> )
        >>> d = cux_df.dashboard(
        >>>    [line_chart_1, line_chart_2],
        >>>    layout=cuxfilter.layouts.double_feature
        >>> )
        >>> # d.app() for serving within notebook cell,
        >>> # d.show() for serving as a separate web-app
        >>> d.app() #or d.show()
        displays interactive dashboard

        >>> queried_df = d.export()
        final query 2<=key<=4


        """
        if (
            len(self._generate_query_str()) > 0
            or self.queried_indices is not None
        ):
            print("final query", self._generate_query_str())
            if self.queried_indices is not None:
                print("polygon selected using lasso selection tool")
            return self._query(self._generate_query_str())
        else:
            print("no querying done, returning original dataframe")
            return self._cuxfilter_df.data

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        template_obj = self._dashboard.generate_dashboard(
            title=self.title,
            charts=self._charts,
            sidebar=self._sidebar,
            theme=self._theme,
            layout_array=self._layout_array,
        )
        cls = "#### cuxfilter " + type(self).__name__
        spacer = "\n    "
        objs = [
            "[%d] %s" % (i, obj.__repr__(1))
            for i, obj in enumerate(template_obj)
        ]
        template = "{cls}{spacer}{spacer}{objs}"
        return template.format(
            cls=cls, objs=("%s" % spacer).join(objs), spacer=spacer
        )

    def _repr_mimebundle_(self, include=None, exclude=None):
        str_repr = self.__repr__()
        server_info = pn.pane.HTML("")
        return pn.Column(str_repr, server_info, width=800)._repr_mimebundle_(
            include, exclude
        )

    def _get_server(
        self,
        panel=None,
        port=0,
        websocket_origin=None,
        loop=None,
        show=False,
        start=False,
        **kwargs,
    ):
        server = get_server(
            panel=panel,
            port=port,
            websocket_origin=websocket_origin,
            loop=loop,
            show=show,
            start=start,
            title=self.title,
            **kwargs,
        )
        server_document(websocket_origin, resources=None)
        return server

    def app(self, sidebar_width=280, width=1200, height=800):
        """
        Run the dashboard with a bokeh backend server within the notebook.

        Parameters
        ----------
        sidebar_width: int, optional, default 280
            width of the sidebar in pixels

        width: int, optional, default 1200
            width of the dashboard in pixels

        height: int, optional, default 800
            height of the dashboard in pixels

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
        >>> d = cux_df.dashboard([line_chart_1])
        >>> d.app(sidebar_width=200, width=1000, height=450)

        """
        self._reinit_all_charts()
        self._current_server_type = "app"

        return self._dashboard.generate_dashboard(
            title=self.title,
            charts=self._charts,
            sidebar=self._sidebar,
            theme=default if self._theme is not None else None,
            layout_array=self._layout_array,
            render_location="notebook",
            sidebar_width=sidebar_width,
            width=width,
            height=height,
        )

    def show(
        self,
        notebook_url=DEFAULT_NOTEBOOK_URL,
        port=0,
        threaded=False,
        service_proxy=None,
        sidebar_width=280,
        height=800,
        **kwargs,
    ):
        """
        Run the dashboard with a bokeh backend server within the notebook.

        Parameters
        ----------

        notebook_url: str, optional, default localhost:8888
            - URL where you want to run the dashboard as a web-app,
            including the port number.

            - Can use localhost instead of ip if running locally.

        port: int, optional
            Has to be an open port

        service_proxy: str, optional, default None,
            available options: jupyterhub

        threaded: boolean, optional, default False
            whether to run the server in threaded mode

        sidebar_width: int, optional, default 280
            width of the sidebar in pixels

        height: int, optional, default 800
            height of the dashboard in pixels

        **kwargs: dict, optional
            additional keyword arguments to pass to the server

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
        >>> d = cux_df.dashboard([line_chart_1])
        >>> d.show(url='localhost:8889')

        """
        if self.server is not None:
            if self.server._started:
                self.stop()
            self._reinit_all_charts()

        self._notebook_url = _get_host(notebook_url)
        if port == 0:
            port = get_open_port()

        dashboard_url = _create_dashboard_url(
            self._notebook_url, port, service_proxy
        )
        print("Dashboard running at port " + str(port))

        panel = self._dashboard.generate_dashboard(
            title=self.title,
            charts=self._charts,
            sidebar=self._sidebar,
            theme=self._theme,
            layout_array=self._layout_array,
            render_location="web-app",
            sidebar_width=sidebar_width,
            height=height,
        )
        try:
            self.server = self._get_server(
                panel=panel,
                port=port,
                websocket_origin=self._notebook_url.netloc,
                show=False,
                start=True,
                threaded=threaded,
                sidebar_width=sidebar_width,
                height=height,
                **kwargs,
            )
        except OSError:
            self.server.stop()
            self.server = self._get_server(
                panel=panel,
                port=port,
                websocket_origin=self._notebook_url.netloc,
                show=False,
                start=True,
                threaded=threaded,
                **kwargs,
            )
        self._current_server_type = "show"
        b = pn.widgets.Button(
            name="open cuxfilter dashboard", button_type="success"
        )
        b.js_on_click(
            args={"target": dashboard_url}, code="window.open(target)"
        )
        return pn.Row(b)

    def stop(self):
        """
        stop the bokeh server
        """
        if self.server._stopped is False:
            self.server.stop()
            self.server._started = False
            self.server._stopped = True
            self.server._tornado.stop()

    def _reload_charts(self, data=None, include_cols=[], ignore_cols=[]):
        """
        Reload charts with current self._cuxfilter_df.data state.
        """
        if data is None:
            # get current data as per the active queries
            data = self._query(self._generate_query_str())
        if len(include_cols) == 0:
            include_cols = self.charts.keys()
        # reloading charts as per current data state
        for chart in self.charts.values():
            if (
                chart.name not in ignore_cols
                and chart.name in include_cols
                and hasattr(chart, "reload_chart")
            ):
                chart.reload_chart(data)
