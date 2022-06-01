from typing import Tuple
import cudf
import cuspatial
import dask.dataframe as dd
import dask_cudf

from ..core_chart import BaseChart
from ....layouts import chart_view
from ...constants import CUXF_DEFAULT_COLOR_PALETTE
from ....assets import cudf_utils


def point_in_polygon(df, x, y, xs, ys):
    return cuspatial.point_in_polygon(
        df[x],
        df[y],
        cudf.Series([0], index=["selection"]),
        [0],
        xs,
        ys,
    )


class BaseGraph(BaseChart):
    """
    .. note::
        Non-aggregate charts do not support Datatiles

    """

    reset_event = None
    x_range: Tuple = None
    y_range: Tuple = None
    selected_indices: cudf.Series = None
    box_selected_range = None
    use_data_tiles = False
    default_palette = CUXF_DEFAULT_COLOR_PALETTE

    @property
    def colors_set(self):
        return self._node_color_palette_input is not None

    @property
    def name(self):
        # overwrite BaseChart name function to allow unique chart on value x
        chart_type = self.chart_type if self.chart_type else "chart"
        return (
            f"{self.node_x}_{self.node_y}_{self.node_id}_"
            f"{self.node_aggregate_fn}_{chart_type}_{self.title}"
        )

    @property
    def node_color_palette(self):
        if self.colors_set:
            return list(self._node_color_palette_input)
        return self.default_palette

    @property
    def edge_columns(self):
        if self.edge_aggregate_col:
            return [
                self.edge_source,
                self.edge_target,
                self.edge_aggregate_col,
            ]
        return [self.edge_source, self.edge_target]

    @property
    def node_columns(self):
        if self.node_aggregate_col:
            return [
                self.node_id,
                self.node_x,
                self.node_y,
                self.node_aggregate_col,
            ]
        return [self.node_id, self.node_x, self.node_y]

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
        node_color_palette=None,
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
        x_axis_tick_formatter=None,
        y_axis_tick_formatter=None,
        unselected_alpha=0.2,
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
            x_axis_tick_formatter
            y_axis_tick_formatter
            unselected_alpha
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
        self.node_aggregate_col = node_aggregate_col or node_id
        self.edge_aggregate_col = edge_aggregate_col
        self.node_aggregate_fn = node_aggregate_fn
        self.edge_aggregate_fn = edge_aggregate_fn
        self._node_color_palette_input = node_color_palette
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
        self.x_axis_tick_formatter = x_axis_tick_formatter
        self.y_axis_tick_formatter = y_axis_tick_formatter
        self.unselected_alpha = unselected_alpha
        self.library_specific_params = library_specific_params

    @property
    def x_dtype(self):
        if isinstance(self.nodes, (cudf.DataFrame, dask_cudf.DataFrame)):
            return self.nodes[self.node_x].dtype
        return None

    @property
    def y_dtype(self):
        if isinstance(self.nodes, (cudf.DataFrame, dask_cudf.DataFrame)):
            return self.nodes[self.node_y].dtype
        return None

    @property
    def df_type(self):
        if type(self.nodes) == type(self.edges):  # noqa: E721
            return type(self.nodes)
        raise TypeError("nodes and edges must be of the same type")

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        self.nodes = dashboard_cls._cuxfilter_df.data

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
        return chart_view(
            self.chart.view(), width=self.width, title=self.title
        )

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

    @property
    def concat(self):
        if self.df_type == dask_cudf.DataFrame:
            return dask_cudf.concat
        return cudf.concat

    def query_graph(self, node_ids, nodes, edges):
        edges_ = self.concat(
            [
                node_ids.merge(
                    edges, left_on=self.node_id, right_on=self.edge_source
                ),
                node_ids.merge(
                    edges, left_on=self.node_id, right_on=self.edge_target
                ),
            ]
        )[self.edge_columns]

        nodes_ = self.concat(
            [
                nodes.merge(
                    edges_,
                    left_on=self.node_id,
                    right_on=self.edge_source,
                ),
                nodes.merge(
                    edges_,
                    left_on=self.node_id,
                    right_on=self.edge_target,
                ),
            ]
        )[self.node_columns].drop_duplicates()

        return nodes_, edges_

    def get_box_select_callback(self, dashboard_cls):
        def cb(bounds, x_selection, y_selection):
            if dashboard_cls._active_view != self:
                # reset previous active view and
                # set current chart as active view
                dashboard_cls._reset_current_view(new_active_view=self)
                self.nodes = dashboard_cls._cuxfilter_df.data

            self.x_range = self._xaxis_dt_transform(x_selection)
            self.y_range = self._yaxis_dt_transform(y_selection)
            # set lasso selected indices to None
            self.selected_indices = None

            query = (
                f"@{self.node_x}_min<={self.node_x}<=@{self.node_x}_max"
                + f" and @{self.node_y}_min<={self.node_y}<=@{self.node_y}_max"
            )
            temp_str_dict = {
                **dashboard_cls._query_str_dict,
                **{self.name: query},
            }
            self.box_selected_range = {
                self.node_x + "_min": self.x_range[0],
                self.node_x + "_max": self.x_range[1],
                self.node_y + "_min": self.y_range[0],
                self.node_y + "_max": self.y_range[1],
            }
            temp_local_dict = {
                **dashboard_cls._query_local_variables_dict,
                **self.box_selected_range,
            }
            nodes = dashboard_cls._query(
                dashboard_cls._generate_query_str(temp_str_dict),
                temp_local_dict,
            )

            edges = None

            if self.inspect_neighbors._active:
                # node_ids = nodes[self.node_id]
                nodes, edges = self.query_graph(nodes, self.nodes, self.edges)

            # reload all charts with new queried data (cudf.DataFrame only)
            dashboard_cls._reload_charts(data=nodes, ignore_cols=[self.name])
            # reload graph chart separately as it has an extra edges argument
            self.reload_chart(data=nodes, edges=edges)
            del nodes, edges

        return cb

    def get_lasso_select_callback(self, dashboard_cls):
        def cb(geometry):
            if dashboard_cls._active_view != self:
                # reset previous active view and
                # set current chart as active view
                dashboard_cls._reset_current_view(new_active_view=self)
                self.nodes = dashboard_cls._cuxfilter_df.data

            xs = self._to_xaxis_type(geometry[:, 0])
            ys = self._to_yaxis_type(geometry[:, 1])

            # set box selected ranges to None
            self.x_range, self.y_range, self.box_selected_range = (
                None,
                None,
                None,
            )

            args = (
                self.node_x,
                self.node_y,
                xs,
                ys,
            )
            # convert datetime to int64 since, point_in_polygon does not
            # support datetime
            if isinstance(self.nodes, dask_cudf.DataFrame):
                self.selected_indices = (
                    self.nodes.assign(
                        **{
                            self.node_x: self._to_xaxis_type(
                                self.nodes[self.node_x]
                            ),
                            self.node_y: self._to_yaxis_type(
                                self.nodes[self.node_y]
                            ),
                        }
                    )
                    .map_partitions(point_in_polygon, *args)
                    .persist()
                )
            else:
                self.selected_indices = point_in_polygon(self.nodes, *args)

            nodes = dashboard_cls._query(
                dashboard_cls._generate_query_str(),
                local_indices=self.selected_indices.selection,
            )
            edges = None

            if self.inspect_neighbors._active:
                # node_ids = nodes[self.node_id]
                nodes, edges = self.query_graph(nodes, self.nodes, self.edges)

            # reload all charts with new queried data (cudf.DataFrame only)
            dashboard_cls._reload_charts(data=nodes, ignore_cols=[self.name])

            # reload graph chart separately as it has an extra edges argument
            self.reload_chart(data=nodes, edges=edges)
            del nodes, edges

        return cb

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        Description:

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        """
        if self.box_selected_range:
            query_str_dict[self.name] = (
                f"@{self.node_x}_min<={self.node_x}<=@{self.node_x}_max"
                + f" and @{self.node_y}_min<={self.node_y}<=@{self.node_y}_max"
            )
            temp_local_dict = {
                self.node_x + "_min": self.x_range[0],
                self.node_x + "_max": self.x_range[1],
                self.node_y + "_min": self.y_range[0],
                self.node_y + "_max": self.y_range[1],
            }
            query_local_variables_dict.update(temp_local_dict)
        else:
            if self.selected_indices is not None:
                query_str_dict[self.name] = self.selected_indices
            else:
                query_str_dict.pop(self.name, None)

            for key in [
                self.node_x + "_min",
                self.node_x + "_max",
                self.node_y + "_min",
                self.node_y + "_max",
            ]:
                query_local_variables_dict.pop(key, None)

    def add_events(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if self.add_interaction:
            self.chart.add_lasso_select_callback(
                self.get_lasso_select_callback(dashboard_cls)
            )
            self.chart.add_box_select_callback(
                self.get_box_select_callback(dashboard_cls)
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

        def reset_callback(resetting):
            if dashboard_cls._active_view != self:
                # reset previous active view and set current
                # chart as active view
                dashboard_cls._reset_current_view(new_active_view=self)
            self.selected_indices = None
            self.box_selected_range = None
            self.chart.reset_all_selections()
            dashboard_cls._query_str_dict.pop(self.name, None)

            nodes = dashboard_cls._query(dashboard_cls._generate_query_str())
            dashboard_cls._reload_charts(nodes)
            # reload graph chart separately as it has an extra edges argument
            self.reload_chart(data=nodes)
            del nodes

        # add callback to reset chart button
        self.chart.add_reset_event(reset_callback)

    def _compute_source(self, query, local_dict, indices):
        return cudf_utils.query_df(self.nodes, query, local_dict, indices)

    def query_chart_by_range(
        self,
        active_chart: BaseChart,
        query_tuple,
        datatile=None,
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
            4. query: query string representing the current filtered state of
                    the dashboard
            5. local_dict: dictionary containing the variable:value mapping
                    local to the query_string.
                    Passed as a parameter to cudf.query() api
            6. indices: cudf.Series representing the current filtered state
                    of the dashboard, apart from the query_string,
                    since the lasso_select callback results in a boolean mask
        -------------------------------------------

        Ouput:
        """
        min_val, max_val = query_tuple
        final_query = f"@min_val<={active_chart.x}<=@max_val"
        local_dict.update({"min_val": min_val, "max_val": max_val})
        if len(query) > 0:
            final_query += f" and {query}"
        self.reload_chart(
            self._compute_source(final_query, local_dict, indices),
        )

    def query_chart_by_indices(
        self,
        active_chart: BaseChart,
        old_indices,
        new_indices,
        datatile=None,
        query="",
        local_dict={},
        indices=None,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. old_indices: list of indices selected in previous callback
            3. new_indices: list of indices selected in currently
            4. datatile: None in case of Geo scatter charts
            5. query: query string representing the current filtered state of
                    the dashboard
            6. local_dict: dictionary containing the variable:value mapping
                    local to the query_string.
                    Passed as a parameter to cudf.query() api
            7. indices: cudf.Series representing the current filtered state
                    of the dashboard, apart from the query_string,
                    since the lasso_select callback results in a boolean mask
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
            final_query = f"{active_chart.x}=={str(float(new_indices[0]))}"
            if len(query) > 0:
                final_query += f" and {query}"
        else:
            new_indices_str = ",".join(map(str, new_indices))
            final_query = f"{active_chart.x} in ({new_indices_str})"
            if len(query) > 0:
                final_query += f" and {query}"

        self.reload_chart(
            self._compute_source(final_query, local_dict, indices)
        )

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
