import panel as pn

from .core_non_aggregate import BaseNonAggregate
from ....layouts import chart_view
from ...constants import BOOL_MAP, CUDF_DATETIME_TYPES
from ....assets.cudf_utils import get_min_max


class BaseLine(BaseNonAggregate):
    stride = 0.0
    reset_event = None
    filter_widget = None
    x_axis_tick_formatter = None
    default_color = "#8735fb"

    @property
    def color_set(self):
        return self._color_input is not None

    @property
    def color(self):
        if self.color_set:
            return self._color_input
        return self.default_color

    def __init__(
        self,
        x,
        y,
        data_points=100,
        add_interaction=True,
        pixel_shade_type="linear",
        color=None,
        step_size=None,
        step_size_type=int,
        width=800,
        height=400,
        title="",
        timeout=100,
        x_axis_tick_formatter=None,
        y_axis_tick_formatter=None,
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
            width
            height
            step_size
            step_size_type
            x_label_map
            y_label_map
            width
            height
            title
            timeout
            x_axis_tick_formatter
            y_axis_tick_formatter
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = x
        self.y = y
        self.data_points = data_points
        self.add_interaction = add_interaction
        self._color_input = color
        self.stride = step_size
        self.stride_type = step_size_type
        self.pixel_shade_type = pixel_shade_type
        self.title = title
        self.timeout = timeout
        self.x_axis_tick_formatter = x_axis_tick_formatter
        self.y_axis_tick_formatter = y_axis_tick_formatter
        self.library_specific_params = library_specific_params
        self.width = width
        self.height = height

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
            self.stride = self.stride_type(stride)

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        self.calculate_source(dashboard_cls._cuxfilter_df.data)

        if self.data_points > len(dashboard_cls._cuxfilter_df.data):
            self.data_points = len(dashboard_cls._cuxfilter_df.data)

        if self.x_dtype == "bool":
            self.min_value = 0
            self.max_value = 1
            self.stride = 1
            # set axis labels:
            if len(self.x_label_map) == 0:
                self.x_label_map = BOOL_MAP
            if len(self.y_label_map) == 0:
                self.y_label_map = BOOL_MAP
        else:
            self.compute_min_max(dashboard_cls)
            self.compute_stride()

        self.generate_chart()
        self.apply_mappers()

        if self.add_interaction:
            self.add_range_slider_filter(dashboard_cls)
        self.add_events(dashboard_cls)

    def view(self):
        return chart_view(
            self.chart, self.filter_widget, width=self.width, title=self.title
        )

    def add_range_slider_filter(self, dashboard_cls):
        """
        Description: add range slider to the bottom of the chart,
                     for the filter function to facilitate interaction
                     behavior, that updates the rest
                     of the charts on the page, using datatiles
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if self.x_dtype in CUDF_DATETIME_TYPES:
            self.filter_widget = pn.widgets.DateRangeSlider(
                start=self.min_value,
                end=self.max_value,
                value=(self.min_value, self.max_value),
                width=self.width,
                sizing_mode="scale_width",
            )
        else:
            self.filter_widget = pn.widgets.RangeSlider(
                start=self.min_value,
                end=self.max_value,
                value=(self.min_value, self.max_value),
                step=self.stride,
                width=self.width,
                sizing_mode="scale_width",
            )

        def filter_widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles()
            query_tuple = self._xaxis_np_dt64_transform(event.new)
            dashboard_cls._query_datatiles_by_range(query_tuple)

        # add callback to filter_Widget on value change
        self.filter_widget.param.watch(
            filter_widget_callback, ["value"], onlychanged=False
        )

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        Description:

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        """
        if self.filter_widget.value != (
            self.filter_widget.start,
            self.filter_widget.end,
        ):
            min_temp, max_temp = self.filter_widget.value
            query_str_dict[
                self.name
            ] = f"@{self.x}_min <= {self.x} <= @{self.x}_max"
            temp_local_dict = {
                self.x + "_min": min_temp,
                self.x + "_max": max_temp,
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
            self.filter_widget.value = (
                self.filter_widget.start,
                self.filter_widget.end,
            )

        # add callback to reset chart button
        self.add_event(self.reset_event, reset_callback)
