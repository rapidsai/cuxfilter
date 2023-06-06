from typing import Tuple
import cudf
import dask_cudf
import dask.dataframe as dd

from .utils import point_in_polygon
from ..core_chart import BaseChart
from ....layouts import chart_view
from ....assets import cudf_utils


class BaseNonAggregate(BaseChart):
    """
    No datatiles support in non_data_tiles plot charts

    If dataset size is greater than a few thousand points,
    scatter geos can crash the browser tabs, and is only recommended
    with datashader plugin, in which case an image is
    rendered instead of points on canvas
    """

    reset_event = None
    x_range: Tuple = None
    y_range: Tuple = None
    selected_indices: cudf.Series = None
    box_selected_range = None
    aggregate_col = None
    use_data_tiles = False

    @property
    def name(self):
        # overwrite BaseChart name function to allow unique chart on value x
        chart_type = self.chart_type if self.chart_type else "chart"
        return (
            f"{self.x}_{self.y}"
            f"{'_'+self.aggregate_col if self.aggregate_col else ''}"
            f"{'_'+self.aggregate_fn if self.aggregate_fn else ''}"
            f"_{chart_type}_{self.title}"
        )

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        if self.x_range is None:
            self.x_range = (
                dashboard_cls._cuxfilter_df.data[self.x].min(),
                dashboard_cls._cuxfilter_df.data[self.x].max(),
            )
        if self.y_range is None:
            self.y_range = (
                dashboard_cls._cuxfilter_df.data[self.y].min(),
                dashboard_cls._cuxfilter_df.data[self.y].max(),
            )
        if isinstance(dashboard_cls._cuxfilter_df.data, dask_cudf.DataFrame):
            self.x_range = dd.compute(*self.x_range)
            self.y_range = dd.compute(*self.y_range)
        self.calculate_source(dashboard_cls._cuxfilter_df.data)
        self.generate_chart()
        self.add_events(dashboard_cls)

    def view(self):
        return chart_view(
            self.chart.view(),
            width=self.width,
            title=self.title,
        )

    def update_dimensions(self, **kwargs):
        pass

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
        def cb(bounds, x_selection, y_selection):
            self.x_range = self._xaxis_dt_transform(x_selection)
            self.y_range = self._yaxis_dt_transform(y_selection)
            # set lasso selected indices to None
            self.selected_indices = None

            self.box_selected_range = {
                self.x + "_min": self.x_range[0],
                self.x + "_max": self.x_range[1],
                self.y + "_min": self.y_range[0],
                self.y + "_max": self.y_range[1],
            }

            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            # reload all charts with new queried data (cudf.DataFrame only)
            dashboard_cls._reload_charts()

        return cb

    def get_lasso_select_callback(self, dashboard_cls):
        def cb(geometry):
            self.source = dashboard_cls._cuxfilter_df.data

            # set box selected ranges to None
            self.x_range, self.y_range, self.box_selected_range = (
                None,
                None,
                None,
            )

            args = (self.x, self.y, geometry)

            if isinstance(self.source, dask_cudf.DataFrame):
                self.selected_indices = (
                    self.source.assign(
                        **{
                            self.x: self._to_xaxis_type(self.source[self.x]),
                            self.y: self._to_yaxis_type(self.source[self.y]),
                        }
                    )
                    .map_partitions(
                        point_in_polygon,
                        *args,
                    )
                    .persist()
                )
            else:
                self.selected_indices = point_in_polygon(self.source, *args)

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
            query_str_dict[self.name] = (
                f"@{self.x}_min<={self.x}<=@{self.x}_max"
                + f" and @{self.y}_min<={self.y}<=@{self.y}_max"
            )
            query_local_variables_dict.update(self.box_selected_range)
        else:
            if self.selected_indices is not None:
                query_str_dict[self.name] = self.selected_indices
            else:
                query_str_dict.pop(self.name, None)

            for key in [
                self.x + "_min",
                self.x + "_max",
                self.y + "_min",
                self.y + "_max",
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
        # def reset_callback():
        def reset_callback(resetting):
            self.selected_indices = None
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
