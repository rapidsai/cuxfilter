from ..core.non_aggregate import (
    BaseScatter,
    BaseLine,
    BaseStackedLine,
    BaseGraph,
)
from .custom_extensions import (
    CustomInspectTool,
    calc_connected_edges,
    InteractiveDatashaderPoints,
    InteractiveDatashaderLine,
    InteractiveDatashaderGraph,
    InteractiveDatashaderMultiLine,
)

from packaging.version import Version
import datashader as ds
import dask_cudf
import dask.dataframe as dd
import cupy as cp
import cudf
import holoviews as hv
from bokeh import events
from PIL import Image
import requests
from io import BytesIO

ds_version = Version(ds.__version__)


def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


class Scatter(BaseScatter):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"

    def format_source_data(self, data):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        self.source = data

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if not self.title:
            self.title = (
                "Scatter plot for "
                + (self.aggregate_col or "")
                + " "
                + self.aggregate_fn
            )

        self.chart = InteractiveDatashaderPoints(
            source_df=self.source,
            x=self.x,
            y=self.y,
            aggregate_col=self.aggregate_col,
            aggregate_fn=self.aggregate_fn,
            color_palette=self.color_palette,
            pixel_shade_type=self.pixel_shade_type,
            tile_provider=self.tile_provider,
            legend=self.legend,
            legend_position=self.legend_position,
            spread_threshold=self.pixel_density,
            point_shape=self.point_shape,
            max_px=self.point_size,
            unselected_alpha=self.unselected_alpha,
        )

    def reload_chart(self, data=None, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in data.columns})
            self.chart.update_data(data)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.colors_set:
            self.chart.color_palette = theme.color_palette
            self.chart._compute_datashader_assets()


class Graph(BaseGraph):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "node_y"
    data_x_axis = "node_x"

    def format_source_data(self, dataframe):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        if isinstance(dataframe, cudf.DataFrame):
            self.nodes = dataframe
        else:
            self.nodes = dataframe.data
            self.edges = dataframe.edges

        if self.edges is not None:
            # update connected_edges value for datashaded edges
            self.connected_edges = calc_connected_edges(
                self.nodes,
                self.edges,
                self.node_x,
                self.node_y,
                self.node_id,
                self.edge_source,
                self.edge_target,
                self.edge_aggregate_col,
                self.x_dtype,
                self.y_dtype,
                self.edge_render_type,
                self.curve_params,
            )

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if not self.title:
            self.title = "Graph"

        impath = (
            "https://raw.githubusercontent.com/rapidsai/cuxfilter/"
            + "branch-0.15/python/cuxfilter/charts/datashader/icons/graph.png"
        )

        self.inspect_neighbors = CustomInspectTool(
            icon=load_image(impath),
            _active=True,
            tool_name="Inspect Neighboring Edges",
        )
        # loading icon from a url
        impath = (
            "https://raw.githubusercontent.com/rapidsai/cuxfilter/"
            + "branch-0.15/python/cuxfilter/charts/datashader/icons/XPan.png"
        )
        self.display_edges = CustomInspectTool(
            icon=load_image(impath), _active=True, tool_name="Display Edges"
        )

        def cb(attr, old, new):
            if not new:
                self.chart.edges_chart.update_data(
                    self.connected_edges.head(0)
                )
            else:
                self.chart.edges_chart.update_data(self.connected_edges)

        self.display_edges.on_change("_active", cb)

        self.chart = InteractiveDatashaderGraph(
            nodes_df=self.nodes,
            edges_df=self.connected_edges,
            node_x=self.node_x,
            node_y=self.node_y,
            node_aggregate_col=self.node_aggregate_col,
            node_aggregate_fn=self.node_aggregate_fn,
            node_color_palette=self.node_color_palette,
            node_pixel_shade_type=self.node_pixel_shade_type,
            tile_provider=self.tile_provider,
            legend=self.legend,
            legend_position=self.legend_position,
            node_spread_threshold=self.node_pixel_density,
            node_point_shape=self.node_point_shape,
            node_max_px=self.node_point_size,
            edge_source="x",
            edge_target="y",
            edge_color=self.edge_color_palette[0],
            edge_transparency=self.edge_transparency,
            inspect_neighbors=self.inspect_neighbors,
            display_edges=self.display_edges,
            unselected_alpha=self.unselected_alpha,
        )

    def reload_chart(self, data, edges=None, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in self.nodes.columns})

        # update connected_edges value for datashaded edges
        # if display edge toggle is active
        if self.display_edges._active:
            self.connected_edges = calc_connected_edges(
                data,
                self.edges if edges is None else edges,
                self.node_x,
                self.node_y,
                self.node_id,
                self.edge_source,
                self.edge_target,
                self.edge_aggregate_col,
                self.x_dtype,
                self.y_dtype,
                self.edge_render_type,
                self.curve_params,
            )
            self.chart.update_data(data, self.connected_edges)
        else:
            self.chart.update_data(data)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.colors_set:
            self.default_palette = theme.color_palette
            self.chart.update_color_palette(theme.color_palette)


class Line(BaseLine):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"
    use_data_tiles = False

    def calculate_source(self, data):
        """
        Description:

        -------------------------------------------
        Input:
        data = cudf.DataFrame
        -------------------------------------------

        Ouput:
        """
        self.format_source_data(data)

    def format_source_data(self, data):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        self.source = data

        self.x_range = (self.source[self.x].min(), self.source[self.x].max())
        self.y_range = (self.source[self.y].min(), self.source[self.y].max())

        if isinstance(data, dask_cudf.core.DataFrame):
            self.x_range = dd.compute(*self.x_range)
            self.y_range = dd.compute(*self.y_range)

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if not self.title:
            if self.x == self.y:
                self.title = "Line plot for " + self.x
            else:
                self.title = "Line plot for (" + self.x + "," + self.y + ")"

        self.chart = InteractiveDatashaderLine(
            source_df=self.source,
            x=self.x,
            y=self.y,
            color=self.color,
            pixel_shade_type=self.pixel_shade_type,
            unselected_alpha=self.unselected_alpha,
        )

    def reload_chart(self, data, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in data.columns})
            self.chart.update_data(data)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.color_set:
            self.default_color = theme.chart_color
            self.chart.color = theme.chart_color


class StackedLines(BaseStackedLine):
    """
    Description:
    """

    reset_event = events.Reset
    data_y_axis = "y"
    data_x_axis = "x"

    def compute_legend(self, colors=None):
        colors = colors or self.colors
        if self.legend:
            res = []
            for i, val in enumerate(colors):
                res.append((self.y[i], val))
            return hv.NdOverlay(
                {
                    k: hv.Curve(
                        self.source.head(1),
                        label=str(k),
                        kdims=[self.x],
                        vdims=[self.y[0]],
                    ).opts(color=v)
                    for k, v in res
                }
            ).opts(legend_position=self.legend_position)
        return None

    def calculate_source(self, data):
        """
        Description:

        -------------------------------------------
        Input:
        data = cudf.DataFrame
        -------------------------------------------

        Ouput:
        """
        self.format_source_data(data)

    def format_source_data(self, data):
        """
        Description:
            format source
        -------------------------------------------
        Input:
        source_dict = {
            'X': [],
            'Y': []
        }
        -------------------------------------------

        Ouput:
        """
        self.source = data
        if self.x_range is None:
            self.x_range = (
                self.source[self.x].min(),
                self.source[self.x].max(),
            )
        if self.y_range is None:
            # cudf_df[['a','b','c']].min().min() gives min value
            # between all values in columns a,b and c

            self.y_range = (
                self.source[self.y].min().min(),
                self.source[self.y].max().max(),
            )
        if isinstance(data, dask_cudf.core.DataFrame):
            self.x_range = dd.compute(*self.x_range)
            self.y_range = dd.compute(*self.y_range)

    def generate_chart(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if not self.title:
            self.title = "Stacked Line plots on x-axis: " + self.x

        self.chart = InteractiveDatashaderMultiLine(
            source_df=self.source,
            x=self.x,
            line_dims=self.y,
            colors=self.colors,
            legend=self.compute_legend(),
            unselected_alpha=self.unselected_alpha,
        )

    def reload_chart(self, data, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if data is not None:
            if len(data) == 0:
                data = cudf.DataFrame({k: cp.nan for k in data.columns})
            self.chart.update_data(data)

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        if not self.colors_set:
            self.default_colors = [theme.chart_color]
            self.chart.legend = self.compute_legend(self.default_colors)
            self.chart.colors = self.default_colors
