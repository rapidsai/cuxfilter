from typing import Tuple
import dask_cudf
import cudf
import cuspatial
import dask.dataframe as dd

from ..core_chart import BaseChart
from ....layouts import chart_view
from ...constants import CUXF_DEFAULT_COLOR_PALETTE


class BaseGraph(BaseChart):
    """
        .. note::
            Non-aggregate charts do not support Datatiles

    """

    reset_event = None
    x_range: Tuple = None
    y_range: Tuple = None
    use_data_tiles = False

    def __init__(
        self,
        node_x="x",
        node_y="y",
        node_id="vertex",
        edge_source="source",
        edge_target="target",
        x_range=None,
        y_range=None,
        add_interaction=True,
        node_aggregate_col=None,
        edge_aggregate_col=None,
        node_aggregate_fn="count",
        edge_aggregate_fn="count",
        node_color_palette=CUXF_DEFAULT_COLOR_PALETTE,
        edge_color_palette=["#000000"],
        node_point_size=1,
        node_point_shape="circle",
        node_pixel_shade_type="eq_hist",
        node_pixel_density=0.5,
        node_pixel_spread="dynspread",
        edge_render_type="direct",
        edge_transparency=0,
        curve_params=dict(strokeWidth=1, curve_total_steps=100),
        tile_provider="CARTODBPOSITRON",
        width=800,
        height=400,
        title="",
        timeout=100,
        legend=True,
        legend_position="center",
        **library_specific_params,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            node_x
            node_y
            node_id
            edge_source
            edge_target
            x_range
            y_range
            add_interaction
            node_aggregate_col
            edge_aggregate_col
            node_aggregate_fn
            edge_aggregate_fn
            node_color_palette
            edge_color_palette
            node_point_size
            node_point_shape
            node_pixel_shade_type
            node_pixel_density
            node_pixel_spread
            edge_render_type
            edge_transparency
            curve_params
            tile_provider
            width
            height
            title
            timeout
            legend
            legend_position
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = node_x
        self.node_x = node_x
        self.node_y = node_y
        self.node_id = node_id
        self.edge_source = edge_source
        self.edge_target = edge_target
        self.x_range = x_range
        self.y_range = y_range
        self.add_interaction = add_interaction
        if node_aggregate_col is not None:
            self.node_aggregate_col = node_aggregate_col
        else:
            self.node_aggregate_col = node_id

        self.edge_aggregate_col = edge_aggregate_col
        self.node_aggregate_fn = node_aggregate_fn
        self.edge_aggregate_fn = edge_aggregate_fn
        self.node_color_palette = list(node_color_palette)
        self.edge_color_palette = list(edge_color_palette)
        self.node_point_size = node_point_size
        self.node_point_shape = node_point_shape
        self.node_pixel_shade_type = node_pixel_shade_type
        self.node_pixel_density = node_pixel_density
        self.node_pixel_spread = node_pixel_spread
        self.edge_render_type = edge_render_type
        self.edge_transparency = edge_transparency
        self.curve_params = curve_params
        self.tile_provider = tile_provider
        self.width = width
        self.height = height
        self.title = title
        self.timeout = timeout
        self.legend = legend
        self.legend_position = legend_position
        self.library_specific_params = library_specific_params

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        if dashboard_cls._cuxfilter_df.edges is None:
            raise ValueError("Edges dataframe not provided")
        if self.x_range is None:
            self.x_range = (
                dashboard_cls._cuxfilter_df.data[self.node_x].min(),
                dashboard_cls._cuxfilter_df.data[self.node_x].max(),
            )
        if self.y_range is None:
            self.y_range = (
                dashboard_cls._cuxfilter_df.data[self.node_y].min(),
                dashboard_cls._cuxfilter_df.data[self.node_y].max(),
            )
        if isinstance(
            dashboard_cls._cuxfilter_df.data, dask_cudf.core.DataFrame
        ):
            self.x_range = dd.compute(*self.x_range)
            self.y_range = dd.compute(*self.y_range)

        self.calculate_source(dashboard_cls._cuxfilter_df)
        self.generate_chart()
        self.add_events(dashboard_cls)

    def view(self):
        return chart_view(self.chart, width=self.width)

    def calculate_source(self, cuxfilter_df):
        """
        Description:

        -------------------------------------------
        Input:
        _cuxfilter_df = cuxfilter.DataFrame (nodes,edges)
        -------------------------------------------

        Ouput:
        """
        self.format_source_data(cuxfilter_df)

    def query_graph(self, node_ids, nodes, edges):
        edges_ = edges.loc[
            cudf.logical_or(
                edges[self.edge_source].isin(node_ids),
                edges[self.edge_target].isin(node_ids),
            ).values
        ]
        if edges_.shape[0] == 0:
            nodes = nodes.loc[nodes[self.node_id].isin(node_ids).values]
        else:
            edges = edges_
            nodes = nodes.loc[
                cudf.logical_or(
                    nodes[self.node_id].isin(edges[self.edge_source]),
                    nodes[self.node_id].isin(edges[self.edge_target]),
                ).values
            ]
        return nodes, edges

    def get_selection_geometry_callback(self, dashboard_cls):
        """
        Description: generate callback for map selection event
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:

        """

        def lasso_callback(xs, ys):
            indices = cuspatial.point_in_polygon(
                self.nodes[self.node_x],
                self.nodes[self.node_y],
                cudf.Series([0], index=["selection"]),
                [0],
                xs,
                ys,
            )
            nodes = self.source[indices.selection]

            if self.inspect_neighbors._active:
                node_ids = nodes[self.node_id]
                nodes, edges = self.query_graph(
                    node_ids, self.nodes, self.edges
                )
            else:
                edges = None

            # reload all charts with new queried data (cudf.DataFrame only)
            dashboard_cls._reload_charts(data=nodes, ignore_cols=[self.name])

            # reload graph chart separately as it has an extra edges argument
            self.reload_chart(nodes=nodes, edges=edges)
            del nodes, edges

        def box_callback(xmin, xmax, ymin, ymax):
            self.x_range = (xmin, xmax)
            self.y_range = (ymin, ymax)

            query = (
                str(xmin)
                + "<="
                + self.node_x
                + " <= "
                + str(xmax)
                + " and "
                + str(ymin)
                + "<="
                + self.node_y
                + " <= "
                + str(ymax)
            )

            dashboard_cls._query_str_dict[self.name] = query
            nodes = dashboard_cls._query(dashboard_cls._generate_query_str())

            if self.inspect_neighbors._active:
                node_ids = nodes[self.node_id]
                nodes, edges = self.query_graph(
                    node_ids, self.nodes, self.edges
                )
            else:
                edges = None

            # reload all charts with new queried data (cudf.DataFrame only)
            dashboard_cls._reload_charts(data=nodes, ignore_cols=[self.name])

            # reload graph chart separately as it has an extra edges argument
            self.reload_chart(nodes=nodes, edges=edges)
            del nodes, edges

        def selection_callback(event):
            if dashboard_cls._active_view != self.name:
                # reset previous active view and
                # set current chart as active view
                dashboard_cls._reset_current_view(new_active_view=self)
                self.source = dashboard_cls._cuxfilter_df.data

            if event.geometry["type"] == "rect":
                xmin, xmax = event.geometry["x0"], event.geometry["x1"]
                ymin, ymax = event.geometry["y0"], event.geometry["y1"]
                box_callback(xmin, xmax, ymin, ymax)
            elif event.geometry["type"] == "poly" and event.final:
                xs = event.geometry["x"]
                ys = event.geometry["y"]
                lasso_callback(xs, ys)

        return selection_callback

    def compute_query_dict(self, query_str_dict):
        """
        Description:

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        """
        if self.x_range is not None and self.y_range is not None:
            query_str_dict[self.name] = (
                str(self.x_range[0])
                + "<="
                + self.node_x
                + " <= "
                + str(self.x_range[1])
                + " and "
                + str(self.y_range[0])
                + "<="
                + self.node_y
                + " <= "
                + str(self.y_range[1])
            )
        else:
            query_str_dict.pop(self.name, None)

    def add_events(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if self.add_interaction:
            self.add_selection_geometry_event(
                self.get_selection_geometry_callback(dashboard_cls)
            )
        if self.reset_event is not None:
            self.add_reset_event(dashboard_cls)

    def add_reset_event(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def reset_callback(event):
            if dashboard_cls._active_view != self.name:
                # reset previous active view and set current
                # chart as active view
                dashboard_cls._reset_current_view(new_active_view=self)
            self.x_range = None
            self.y_range = None
            dashboard_cls._query_str_dict.pop(self.name, None)

            nodes = dashboard_cls._query(dashboard_cls._generate_query_str())
            dashboard_cls._reload_charts(nodes)
            # reload graph chart separately as it has an extra edges argument
            self.reload_chart(nodes=nodes)
            del nodes

        # add callback to reset chart button
        self.add_event(self.reset_event, reset_callback)

    def query_chart_by_range(
        self, active_chart: BaseChart, query_tuple, datatile=None, query=""
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
        self.reload_chart(self.nodes.query(final_query))

    def query_chart_by_indices(
        self,
        active_chart: BaseChart,
        old_indices,
        new_indices,
        datatile=None,
        query="",
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
            self.reload_chart(self.nodes)
        elif len(new_indices) == 1:
            final_query = active_chart.x + "==" + str(float(new_indices[0]))
            if len(query) > 0:
                final_query += " and " + query
            # just a single index
            self.reload_chart(self.nodes.query(final_query))
        else:
            new_indices_str = ",".join(map(str, new_indices))
            final_query = active_chart.x + " in (" + new_indices_str + ")"
            if len(query) > 0:
                final_query += " and " + query
            self.reload_chart(self.nodes.query(final_query))

    def add_selection_geometry_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        # ('function to be overridden by library specific extensions')

    def reset_chart_geometry_ranges(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        # ('function to be overridden by library specific extensions')
