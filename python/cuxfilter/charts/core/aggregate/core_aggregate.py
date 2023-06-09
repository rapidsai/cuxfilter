import panel as pn
import numpy as np
from bokeh.models import DatetimeTickFormatter

from ..core_chart import BaseChart
from ....assets.numba_kernels import calc_groupby, calc_value_counts
from ....layouts import chart_view
from ...constants import (
    BOOL_MAP,
    CUDF_DATETIME_TYPES,
)
from ....assets.cudf_utils import get_min_max


class BaseAggregateChart(BaseChart):
    reset_event = None
    filter_widget = None
    x_axis_tick_formatter = None
    y_axis_tick_formatter = None
    use_data_tiles = True
    custom_binning = False
    stride = None
    data_points = None
    _x_dtype = float

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
        width=400,
        height=400,
        step_size=None,
        step_size_type=int,
        title="",
        autoscaling=True,
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
        self.height = height
        self.width = width
        self.title = title if title else self.x
        self.autoscaling = autoscaling
        self.x_axis_tick_formatter = x_axis_tick_formatter
        self.y_axis_tick_formatter = y_axis_tick_formatter
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
        self.x_dtype = dashboard_cls._cuxfilter_df.data[self.x].dtype
        # reset data_point to input _data_points
        self.data_points = self._data_points
        # reset stride to input _stride
        self.stride = self._stride

        if self.x_dtype == "bool":
            self.min_value = 0
            self.max_value = 1
            self.stride = 1
            # set axis labels:
            if len(self.x_label_map) == 0:
                self.x_label_map = BOOL_MAP
            if (
                self.y != self.x
                and self.y is not None
                and len(self.y_label_map) == 0
            ):
                self.y_label_map = BOOL_MAP
        else:
            self.compute_min_max(dashboard_cls)
            if self.x_dtype in CUDF_DATETIME_TYPES:
                self.x_axis_tick_formatter = DatetimeTickFormatter()
            if self.x_dtype != "object":
                self.compute_stride()
            else:
                self.use_data_tiles = False

        self.calculate_source(dashboard_cls._cuxfilter_df.data)
        self.generate_chart()
        self.apply_mappers()

        if self.add_interaction and self.x_dtype != "object":
            self.add_range_slider_filter(dashboard_cls)
        self.add_events(dashboard_cls)

    def view(self):
        return chart_view(
            self.chart, self.filter_widget, width=self.width, title=self.title
        )

    def calculate_source(self, data, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if self.y == self.x or self.y is None:
            # it's a histogram
            df, self.data_points = calc_value_counts(
                data[self.x],
                self.stride,
                self.min_value,
                self.data_points,
                self.custom_binning,
            )
            if self.data_points > 50_000:
                print(
                    "number of x-values for a bar chart ",
                    "exceeds 50,000 points.",
                    "Performance may be laggy, its recommended ",
                    "to use custom data_points parameter to ",
                    "enforce custom binning for smooth crossfiltering",
                )
        else:
            self.aggregate_fn = "mean"
            df = calc_groupby(self, data).to_pandas().to_numpy().transpose()
            if self.data_points is None:
                self.data_points = len(df[0])

        if self.stride is None and self.x_dtype != "object":
            self.compute_stride()

        if self.custom_binning:
            if len(self.x_label_map) == 0:
                temp_mapper_index = np.array(df[0])
                temp_mapper_value = np.round(
                    (temp_mapper_index * self.stride) + self.min_value,
                    4,
                ).astype("str")
                temp_mapper_index = temp_mapper_index.astype("str")
                self.x_label_map = dict(
                    zip(temp_mapper_index, temp_mapper_value)
                )
        dict_temp = {
            "X": df[0],
            "Y": df[1],
        }

        if patch_update and len(dict_temp["X"]) < len(
            self._transformed_source_data(self.data_x_axis)
        ):
            # if not all X axis bins are provided, filling bins not updated
            # with zeros
            y_axis_data = self._compute_array_all_bins(
                self._transformed_source_data(self.data_x_axis),
                dict_temp["X"],
                dict_temp["Y"],
            )

            dict_temp = {
                "X": self._transformed_source_data(self.data_x_axis),
                "Y": y_axis_data,
            }

        self.format_source_data(dict_temp, patch_update)

    def add_range_slider_filter(self, dashboard_cls):
        """
        Description: add range slider to the bottom of the chart,
                    for the filter function to facilitate interaction behavior,
                    that updates the rest of the charts on the page
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
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            dashboard_cls._reload_charts()

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
            query = f"@{self.x}_min <= {self.x} <= @{self.x}_max"
            query_str_dict[self.name] = query
            query_local_variables_dict[self.x + "_min"] = min_temp
            query_local_variables_dict[self.x + "_max"] = max_temp
        else:
            query_str_dict.pop(self.name, None)
            query_local_variables_dict.pop(self.x + "_min", None)
            query_local_variables_dict.pop(self.x + "_max", None)

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
            if self.add_interaction and self.x_dtype != "object":
                self.filter_widget.value = (
                    self.filter_widget.start,
                    self.filter_widget.end,
                )

        # add callback to reset chart button
        self.chart.on_event(self.reset_event, reset_callback)
