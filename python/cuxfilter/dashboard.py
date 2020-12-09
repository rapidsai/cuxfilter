from typing import Dict, Type, Union
import bokeh.embed.util as u
import panel as pn
import uuid
from panel.io.server import get_server
from bokeh.embed import server_document
import os
import urllib

from .charts.core import BaseChart, BaseWidget, ViewDataFrame
from .datatile import DataTile
from .layouts import single_feature
from .charts.panel_widgets import data_size_indicator
from .assets import screengrab, get_open_port
from .themes import light
from IPython.core.display import Image, display
from IPython.display import publish_display_data

_server_info = (
    "<b>Running server:</b>"
    '<a target="_blank" href="https://localhost:{port}">'
    "https://localhost:{port}</a>"
)
EXEC_MIME = "application/vnd.holoviews_exec.v0+json"
HTML_MIME = "text/html"

DEFAULT_NOTEBOOK_URL = "http://localhost:8888"

CUXF_BASE_CHARTS = (BaseChart, BaseWidget, ViewDataFrame)


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


def _create_app(
    panel_obj, notebook_url=DEFAULT_NOTEBOOK_URL, port=0, service_proxy=None,
):
    """
    Displays a bokeh server app inline in the notebook.
    Arguments
    ---------
    notebook_url: str, optional
        URL to the notebook server
    port: int (optional, default=0)
        Allows specifying a specific port
    """
    dashboard_url = _create_dashboard_url(notebook_url, port, service_proxy)

    server_id = uuid.uuid4().hex
    server = get_server(
        panel=panel_obj,
        port=port,
        websocket_origin=notebook_url.netloc,
        start=True,
        show=False,
        server_id=server_id,
    )

    script = server_document(dashboard_url, resources=None)

    publish_display_data(
        {HTML_MIME: script, EXEC_MIME: ""},
        metadata={EXEC_MIME: {"server_id": server_id}},
    )
    return server


class DashBoard:
    """
    A cuxfilter GPU DashBoard object.
    Examples
    --------

    Create a dashboard

    >>> import cudf
    >>> import cuxfilter
    >>> from cuxfilter.charts import bokeh
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
    >>> d = cux_df.dashboard([line_chart_1, line_chart_2])
    >>> d
    `cuxfilter DashBoard
    [title] Markdown(str)
    [chart1] Column(sizing_mode='scale_both', width=1600)
        [0] Bokeh(Figure)
    [chart2] Column(sizing_mode='scale_both', width=1600)
        [0] Bokeh(Figure)`
    """

    _charts: Dict[str, Union[CUXF_BASE_CHARTS]]
    _data_tiles: Dict[str, Type[DataTile]]
    _query_str_dict: Dict[str, str]
    _query_local_variables_dict = {}
    _active_view: str = ""
    _dashboard = None
    _theme = None
    _notebook_url = DEFAULT_NOTEBOOK_URL
    # _current_server_type - show(separate tab)/ app(in-notebook)
    _current_server_type = "show"
    server = None

    def __init__(
        self,
        charts=[],
        dataframe=None,
        layout=single_feature,
        theme=light,
        title="Dashboard",
        data_size_widget=True,
        warnings=False,
    ):
        self._cuxfilter_df = dataframe
        self._charts = dict()
        self._data_tiles = dict()
        self._query_str_dict = dict()
        self.data_size_widget = data_size_widget
        if self.data_size_widget:
            temp_chart = data_size_indicator()
            self._charts[temp_chart.name] = temp_chart
            self._charts[temp_chart.name].initiate_chart(self)

        if len(charts) > 0:
            for chart in charts:
                self._charts[chart.name] = chart
                chart.initiate_chart(self)
                chart._initialized = True

        self.title = title
        self._dashboard = layout()
        self._theme = theme
        # handle dashboard warnings
        if not warnings:
            u.log.disabled = True

    @property
    def charts(self):
        """
        Charts in the dashboard as a dictionary.
        """
        return self._charts

    def add_charts(self, charts=[]):
        """
        Adding more charts to the dashboard, after it has been initialized.
        Parameters
        ----------
        charts: list
            list of cuxfilter.charts objects

        Notes
        -----
            After adding the charts, refresh the dashboard app
            tab to see the updated charts.

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
        >>> line_chart_2 = bokeh.bar(
        >>>     'val', 'key', data_points=5, add_interaction=False
        >>> )
        >>> d.add_charts([line_chart_2])

        """
        self._data_tiles = {}
        if len(self._active_view) > 0:
            self._charts[self._active_view].datatile_loaded_state = False
            self._active_view = ""

        if len(charts) > 0:
            for chart in charts:
                if chart not in self._charts:
                    self._charts[chart.name] = chart
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
        if self.data_size_widget:
            temp_chart = data_size_indicator()
            self._charts[temp_chart.name] = temp_chart
            self._charts[temp_chart.name].initiate_chart(self)

        for chart in self._charts:
            self._charts[chart].source = None
            self._charts[chart].initiate_chart(self)
            self._charts[chart]._initialized = True

    def _query(self, query_str, local_dict=None):
        """
        Query the cudf.DataFrame, inplace or create a copy based on the
        value of inplace.
        """
        local_dict = local_dict or self._query_local_variables_dict
        if len(query_str) > 0:
            return self._cuxfilter_df.data.query(
                query_str, local_dict=local_dict
            )
        else:
            return self._cuxfilter_df.data

    def _generate_query_str(self, query_dict=None, ignore_chart=""):
        """
        Generate query string based on current crossfiltered state of
        the dashboard.
        """
        popped_value = None
        query_dict = query_dict or self._query_str_dict
        if (
            isinstance(ignore_chart, CUXF_BASE_CHARTS)
            and len(ignore_chart.name) > 0
            and ignore_chart.name in query_dict
        ):
            popped_value = query_dict.pop(ignore_chart.name, None)

        return_query_str = " and ".join(list(query_dict.values()))

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
        cudf.DataFrame

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
        >>> d = cux_df.dashboard([line_chart_1, line_chart_2])
        >>> d.app() #or d.show()
        displays dashboard
        do some visual querying/ crossfiltering

        >>> queried_df = d.export()
        final query 2<=key<=4


        """
        # Compute query for currently active chart, and consider its
        # current state as final state
        if self._active_view == "":
            print("no querying done, returning original dataframe")
            # return self._backup_data
            return self._cuxfilter_df.data
        else:
            self._charts[self._active_view].compute_query_dict(
                self._query_str_dict, self._query_local_variables_dict
            )

            if len(self._generate_query_str()) > 0:
                print("final query", self._generate_query_str())
                return self._query(self._generate_query_str())
            else:
                print("no querying done, returning original dataframe")
                return self._cuxfilter_df.data

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        template_obj = self._dashboard.generate_dashboard(
            self.title, self._charts, self._theme
        )
        cls = "#### cuxfilter " + type(self).__name__
        spacer = "\n    "
        objs = [
            "[%s] %s" % (name, obj.__repr__())
            for name, obj in template_obj._render_items.items()
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
        port=0,
        websocket_origin=None,
        loop=None,
        show=False,
        start=False,
        **kwargs,
    ):
        return get_server(
            panel=self._dashboard.generate_dashboard(
                self.title, self._charts, self._theme
            ),
            port=port,
            websocket_origin=websocket_origin,
            loop=loop,
            show=show,
            start=start,
            title=self.title,
            **kwargs,
        )

    async def preview(self):
        """
        Preview(Async) all the charts in a jupyter cell, non interactive(no
        backend server). Mostly intended to save notebook state for blogs,
        documentation while still rendering the dashboard.

        Notes
        -----
        Png format

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
        >>> d = cux_df.dashboard([line_chart_1, line_chart_2])
        >>> await d.preview()
        displays charts in the dashboard
        """
        if self.server is not None:
            if self.server._started:
                self.stop()
            self._reinit_all_charts()
            port = self.server.port
        else:
            port = get_open_port()
        url = "localhost:" + str(port)
        self.server = self._get_server(
            port=port, websocket_origin=url, show=False, start=True
        )
        await screengrab("http://" + url)
        self.stop()

        display(Image("temp.png"))

    def app(
        self,
        notebook_url=DEFAULT_NOTEBOOK_URL,
        port: int = 0,
        service_proxy=None,
    ):
        """
        Run the dashboard with a bokeh backend server within the notebook.
        Parameters
        ----------
        url: str, optional
            url of the notebook(including the port).
            Can use localhost instead of ip if running locally

        port: int, optional
            Port number bokeh uses for it's two communication protocol.
            Default is random open port. Recommended to set this value if
            running jupyter remotely and only few ports are exposed.

        service_proxy: str, optional, default None,
            available options: jupyterhub

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
        >>> d.app(notebook_url='localhost:8888')

        """
        if self.server is not None:
            if self.server._started:
                self.stop()
            self._reinit_all_charts()

        self._notebook_url = _get_host(notebook_url)
        if port == 0:
            port = get_open_port()

        self.server = _create_app(
            self._dashboard.generate_dashboard(
                self.title, self._charts, self._theme
            ),
            notebook_url=self._notebook_url,
            port=port,
            service_proxy=service_proxy,
        )
        self._current_server_type = "app"

    def show(
        self,
        notebook_url=DEFAULT_NOTEBOOK_URL,
        port=0,
        threaded=False,
        service_proxy=None,
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
        port: int,
            optional- Has to be an open port

        service_proxy: str, optional, default None,
            available options: jupyterhub

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

        try:
            self.server = self._get_server(
                port=port,
                websocket_origin=self._notebook_url.netloc,
                show=False,
                start=True,
                threaded=threaded,
                **kwargs,
            )
        except OSError:
            self.server.stop()
            self.server = self._get_server(
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
            include_cols = list(self._charts.keys())
        # reloading charts as per current data state
        for chart in self._charts.values():
            if chart.name not in ignore_cols and chart.name in include_cols:
                self._charts[chart.name].reload_chart(data, patch_update=True)

    def _calc_data_tiles(self, cumsum=True):
        """
        Calculate data tiles for all aggregate type charts.
        """
        # query_str = self._generate_query_str(self._charts[self._active_view])

        # NO DATATILES for scatter types, as they are essentially all
        # points in the dataset
        query = self._generate_query_str(
            ignore_chart=self._charts[self._active_view]
        )

        if "scatter" not in self._active_view:
            for chart in list(self._charts.values()):
                if not chart.use_data_tiles:
                    self._data_tiles[chart.name] = None
                elif self._active_view != chart.name:
                    self._data_tiles[chart.name] = DataTile(
                        self._charts[self._active_view],
                        chart,
                        dtype="pandas",
                        cumsum=cumsum,
                    ).calc_data_tile(self._query(query).copy())

        self._charts[self._active_view].datatile_loaded_state = True

    def _query_datatiles_by_range(self, query_tuple):
        """
        Update each chart using the updated values after querying
        the datatiles using query_tuple.
        Parameters
        ----------
        query_tuple: tuple
            (min_val, max_val) of the query

        """
        for chart in self._charts.values():
            if (
                self._active_view != chart.name
                and "widget" not in chart.chart_type
            ):
                if chart.chart_type == "view_dataframe":
                    chart.query_chart_by_range(
                        self._charts[self._active_view],
                        query_tuple,
                        self._cuxfilter_df.data,
                        self._generate_query_str(
                            self._charts[self._active_view]
                        ),
                        self._query_local_variables_dict,
                    )
                elif not chart.use_data_tiles:
                    chart.query_chart_by_range(
                        self._charts[self._active_view],
                        query_tuple,
                        self._data_tiles[chart.name],
                        self._generate_query_str(
                            ignore_chart=self._charts[self._active_view]
                        ),
                        self._query_local_variables_dict,
                    )
                else:
                    chart.query_chart_by_range(
                        self._charts[self._active_view],
                        query_tuple,
                        self._data_tiles[chart.name],
                    )

    def _query_datatiles_by_indices(self, old_indices, new_indices):
        """
        Update each chart using the updated values after querying the
        datatiles using new_indices.
        """
        for chart in self._charts.values():
            if (
                self._active_view != chart.name
                and "widget" not in chart.chart_type
            ):
                if chart.chart_type == "view_dataframe":
                    chart.query_chart_by_indices(
                        self._charts[self._active_view],
                        old_indices,
                        new_indices,
                        self._cuxfilter_df.data,
                        self._generate_query_str(
                            ignore_chart=self._charts[self._active_view]
                        ),
                        self._query_local_variables_dict,
                    )
                elif not chart.use_data_tiles:
                    chart.query_chart_by_indices(
                        self._charts[self._active_view],
                        old_indices,
                        new_indices,
                        self._data_tiles[chart.name],
                        self._generate_query_str(
                            ignore_chart=self._charts[self._active_view]
                        ),
                        self._query_local_variables_dict,
                    )
                else:
                    chart.query_chart_by_indices(
                        self._charts[self._active_view],
                        old_indices,
                        new_indices,
                        self._data_tiles[chart.name],
                    )

    def _reset_current_view(self, new_active_view: CUXF_BASE_CHARTS):
        """
        Reset current view and assign new view as the active view.
        """
        if len(self._active_view) == 0:
            self._active_view = new_active_view.name
            return -1

        self._charts[self._active_view].compute_query_dict(
            self._query_str_dict, self._query_local_variables_dict
        )

        # resetting the loaded state
        self._charts[self._active_view].datatile_loaded_state = False

        # switching the active view
        self._active_view = new_active_view.name

        self._query_str_dict.pop(self._active_view, None)
        if (
            "widget" not in self._charts[self._active_view].chart_type
            and self._charts[self._active_view].use_data_tiles
        ):
            self._charts[self._active_view].reload_chart(
                data=self._query(
                    self._generate_query_str(
                        ignore_chart=self._charts[self._active_view]
                    )
                ),
                patch_update=True,
            )
