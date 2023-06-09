import cudf
import dask_cudf
from typing import Tuple

from ..core_chart import BaseChart
from ....layouts import chart_view


class BaseStackedLine(BaseChart):
    """
    .. note::
        If dataset size is greater than a few thousand points,
        scatter geos can crash the browser tabs, and is only recommended
        with datashader plugin, in which case an image is
        rendered instead of points on canvas
    """

    reset_event = None
    x_range: Tuple = None
    y_range: Tuple = None
    use_data_tiles = False
    y: list = []
    colors: list = []
    default_colors = ["#8735fb"]
    box_selected_range = None

    @property
    def y_dtype(self):
        """
        overwriting the y_dtype property from BaseChart for stackedLines where
        self.y is a list of columns
        """
        if isinstance(self.source, (cudf.DataFrame, dask_cudf.DataFrame)):
            return self.source[self.y[0]].dtype
        return None

    @property
    def name(self):
        # overwrite BaseChart name function to allow unique chart on value x
        chart_type = self.chart_type if self.chart_type else "chart"
        return (
            f"{self.x}_{'_'.join([str(_i) for _i in self.y])}_{chart_type}"
            f"_{self.title}"
        )

    @property
    def colors_set(self):
        return self._colors_input != []

    @property
    def colors(self):
        if self.colors_set:
            return list(self._colors_input)
        return self.default_colors * len(self.y)

    def __init__(
        self,
        x,
        y=[],
        data_points=100,
        add_interaction=True,
        colors=[],
        step_size=None,
        step_size_type=int,
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
            x,
            y
            data_points
            add_interaction
            colors
            step_size
            step_size_type
            width
            height
            title
            timeout
            legend
            legend_position
            x_axis_tick_formatter
            y_axis_tick_formatter
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = x
        if not isinstance(y, list):
            raise TypeError("y must be a list of column names")
        if len(y) == 0:
            raise ValueError("y must not be empty")
        self.y = y
        self.data_points = data_points
        self.add_interaction = add_interaction
        self.stride = step_size
        if not isinstance(colors, (list, dict)):
            raise TypeError(
                "colors must be either list of colors or"
                + "dictionary of column to color mappings"
            )
        self._colors_input = colors
        self.stride_type = step_size_type
        self.title = title
        self.timeout = timeout
        self.legend = legend
        self.legend_position = legend_position
        self.x_axis_tick_formatter = x_axis_tick_formatter
        self.y_axis_tick_formatter = y_axis_tick_formatter
        self.unselected_alpha = unselected_alpha
        self.library_specific_params = library_specific_params
        self.width = width
        self.height = height

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------
        """
        for _y in self.y:
            if self.y_dtype != dashboard_cls._cuxfilter_df.data[_y].dtype:
                raise TypeError("All y columns should be of same type")

        if self.x_range is None:
            self.x_range = (
                dashboard_cls._cuxfilter_df.data[self.x].min(),
                dashboard_cls._cuxfilter_df.data[self.x].max(),
            )
        if self.y_range is None:
            # cudf_df[['a','b','c']].min().min() gives min value
            # between all values in columns a,b and c
            self.y_range = (
                dashboard_cls._cuxfilter_df.data[self.y].min().min(),
                dashboard_cls._cuxfilter_df.data[self.y].max().max(),
            )
        self.calculate_source(dashboard_cls._cuxfilter_df.data)
        self.generate_chart()
        self.add_events(dashboard_cls)

    def view(self):
        return chart_view(
            self.chart.view(), width=self.width, title=self.title
        )

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

    def get_box_select_callback(self, dashboard_cls):
        def cb(boundsx):
            self.x_range = self._xaxis_dt_transform(boundsx)

            self.box_selected_range = {
                self.x + "_min": self.x_range[0],
                self.x + "_max": self.x_range[1],
            }
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            # reload all charts with new queried data (cudf.DataFrame only)
            dashboard_cls._reload_charts()

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
            query_str_dict[
                self.name
            ] = f"@{self.x}_min<={self.x}<=@{self.x}_max"
            temp_local_dict = {
                self.x + "_min": self.x_range[0],
                self.x + "_max": self.x_range[1],
            }
            query_local_variables_dict.update(temp_local_dict)
        else:
            query_str_dict.pop(self.name, None)
            for key in [self.x + "_min", self.x + "_max"]:
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
            self.box_selected_range = None
            self.chart.reset_all_selections()
            dashboard_cls._query_str_dict.pop(self.name, None)
            dashboard_cls._reload_charts()

        # add callback to reset chart button
        self.chart.add_reset_event(reset_callback)

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
