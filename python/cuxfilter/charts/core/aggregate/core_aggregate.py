import numpy as np
from typing import Union
from bokeh.models import DatetimeTickFormatter
import holoviews as hv
from ..core_chart import BaseChart
from ...constants import (
    CUDF_DATETIME_TYPES,
)
from ....assets.cudf_utils import get_min_max


class BaseAggregateChart(BaseChart):
    reset_event = None
    x_axis_tick_formatter = None
    y_axis_tick_formatter = None
    use_data_tiles = True
    stride = None
    data_points: Union[int, None] = None
    _x_dtype = float
    box_stream = hv.streams.SelectionXY()
    reset_stream = hv.streams.PlotReset()

    @property
    def name(self):
        # overwrite BaseChart name function to allow unique choropleths on
        # value x
        if self.chart_type is not None:
            return (
                f"{self.x}_{self.aggregate_fn}_{self.chart_type}_{self.title}"
            )
        else:
            return f"{self.x}_{self.aggregate_fn}_chart_{self.title}"

    @property
    def x_dtype(self):
        """
        override core_chart x_dtype and make it constant, as panel 0.11 seems
        to update the datetime x_axis type to float during runtime
        """
        return self._x_dtype

    @x_dtype.setter
    def x_dtype(self, value):
        self._x_dtype = value

    @property
    def custom_binning(self):
        return self._stride is not None or self._data_points is not None

    def _transformed_source_data(self, property):
        """
        this fixes a bug introduced with panel 0.11, where bokeh CDS
        x-axis datetime is converted to float, and the only way to
        convert it back to datetime is using datetime64[ms]
        """
        if self.x_dtype in CUDF_DATETIME_TYPES:
            return self.source.data[property].astype("datetime64[ms]")
        return self.source.data[property]

    def __init__(
        self,
        x,
        y=None,
        data_points=None,
        add_interaction=True,
        aggregate_fn="count",
        step_size=None,
        step_size_type=int,
        title="",
        autoscaling=True,
        x_axis_tick_formatter=None,
        y_axis_tick_formatter=None,
        unselected_alpha=0.1,
        **library_specific_params,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            x
            y
            data_points
            add_interaction
            aggregate_fn
            step_size
            step_size_type
            title
            autoscaling
            x_label_map
            y_label_map
            x_axis_tick_formatter
            y_axis_tick_formatter
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = x
        self.y = y
        self._stride = step_size
        self._data_points = data_points
        self.stride_type = step_size_type
        self.add_interaction = add_interaction
        self.aggregate_fn = aggregate_fn
        self.title = title if title else self.x
        self.autoscaling = autoscaling
        self.x_axis_tick_formatter = x_axis_tick_formatter
        self.y_axis_tick_formatter = y_axis_tick_formatter
        self.unselected_alpha = unselected_alpha
        self.library_specific_params = library_specific_params

    def _compute_array_all_bins(self, source_x, update_data_x, update_data_y):
        """
        source_x: current_source_x, np.array()
        update_data_x: updated_data_x, np.array()
        update_data_y: updated_data_x, np.array()
        """
        if self.x_dtype in CUDF_DATETIME_TYPES:
            source_x = source_x.astype("datetime64[ms]")
        result_array = np.zeros(shape=source_x.shape)
        indices = [np.where(x_ == source_x)[0][0] for x_ in update_data_x]
        np.put(result_array, indices, update_data_y)
        return result_array

    def compute_min_max(self, dashboard_cls):
        self.min_value, self.max_value = get_min_max(
            dashboard_cls._cuxfilter_df.data, self.x
        )

    def compute_stride(self):
        self.stride_type = self._xaxis_stride_type_transform(self.stride_type)

        if self.stride_type == int and self.max_value < 1:
            self.stride_type = float

        if self.stride is None and self.data_points is not None:
            raw_stride = (self.max_value - self.min_value) / self.data_points
            stride = (
                round(raw_stride) if self.stride_type == int else raw_stride
            )
            self.stride = stride

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:

        """
        self.x_dtype = dashboard_cls._cuxfilter_df.data[self.x].dtype
        # reset data_point to input _data_points
        self.data_points = self._data_points
        # reset stride to input _stride
        self.stride = self._stride

        if self.x_dtype == "bool":
            self.min_value = 0
            self.max_value = 1
            self.stride = 1
        else:
            self.compute_min_max(dashboard_cls)
            if self.x_dtype in CUDF_DATETIME_TYPES:
                self.x_axis_tick_formatter = DatetimeTickFormatter()
            if self.x_dtype != "object":
                self.compute_stride()

        self.source = dashboard_cls._cuxfilter_df.data
        self.generate_chart()
        self.add_events(dashboard_cls)

    def get_reset_callback(self, dashboard_cls):
        def reset_callback(resetting):
            self.box_selected_range = None
            self.selected_indices = None
            dashboard_cls._query_str_dict.pop(self.name, None)
            dashboard_cls._reload_charts()

        return reset_callback

    def get_box_select_callback(self, dashboard_cls):
        def cb(bounds, x_selection, y_selection):
            self.box_selected_range, self.selected_indices = None, None
            if type(x_selection) == tuple:
                self.box_selected_range = {
                    self.x + "_min": x_selection[0],
                    self.x + "_max": x_selection[1],
                }
            elif type(x_selection) == list:
                self.selected_indices = (
                    dashboard_cls._cuxfilter_df.data[self.x]
                    .isin(x_selection)
                    .reset_index()
                )[[self.x]]

            if self.box_selected_range or self.selected_indices is not None:
                self.compute_query_dict(
                    dashboard_cls._query_str_dict,
                    dashboard_cls._query_local_variables_dict,
                )
                # reload all charts with new queried data (cudf.DataFrame only)
                dashboard_cls._reload_charts()

        return cb

    def get_dashboard_view(self):
        return self.chart.view()

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
            query_local_variables_dict.update(self.box_selected_range)
        else:
            if self.selected_indices is not None:
                query_str_dict[self.name] = self.selected_indices
            else:
                query_str_dict.pop(self.name, None)

            query_local_variables_dict.pop(self.x + "_min", None)
            query_local_variables_dict.pop(self.x + "_max", None)

    def add_events(self, dashboard_cls):
        """
        Description: add events to the chart, for the filter function to
            facilitate interaction behavior,
        that updates the rest of the charts on the page
        -------------------------------------------
        Input:
        - dashboard_cls = current dashboard class reference
        """
        self.chart.add_box_select_callback(
            self.get_box_select_callback(dashboard_cls)
        )
        self.chart.add_reset_callback(self.get_reset_callback(dashboard_cls))
