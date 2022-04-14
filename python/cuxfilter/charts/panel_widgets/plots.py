from cuxfilter.layouts.chart_views import chart_view
from ..core import BaseWidget
from ..core.aggregate import BaseNumberChart
from ..constants import (
    CUDF_DATETIME_TYPES,
    DATATILE_ACTIVE_COLOR,
    DATATILE_INACTIVE_COLOR,
)
from ...assets.cudf_utils import get_min_max
from bokeh.models import ColumnDataSource
import cudf
import dask_cudf
import panel as pn


class RangeSlider(BaseWidget):
    _datatile_loaded_state: bool = False
    datatile_active_color = DATATILE_ACTIVE_COLOR

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = self.datatile_active_color
        else:
            self.chart.bar_color = DATATILE_INACTIVE_COLOR

    def compute_stride(self):
        if self.stride_type == int and self.max_value < 1:
            self.stride_type = float

        if self.stride is None:
            self.stride = self.chart.step

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        self.min_value, self.max_value = get_min_max(
            dashboard_cls._cuxfilter_df.data, self.x
        )

        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        """
        generate widget range slider
        """
        if self.stride:
            self.params["step"] = self.stride

        self.chart = pn.widgets.RangeSlider(
            start=self.min_value,
            end=self.max_value,
            value=(self.min_value, self.max_value),
            **self.params,
        )
        self.compute_stride()

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        # interactive slider
        self.datatile_active_color = theme.datatile_active_color

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles()

            query_tuple = self._xaxis_np_dt64_transform(event.new)
            dashboard_cls._query_datatiles_by_range(query_tuple)

        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if self.chart.value != (self.chart.start, self.chart.end):
            min_temp, max_temp = self.chart.value
            query = f"@{self.x}_min<={self.x}<=@{self.x}_max"
            query_str_dict[self.name] = query
            query_local_variables_dict[self.x + "_min"] = min_temp
            query_local_variables_dict[self.x + "_max"] = max_temp
        else:
            query_str_dict.pop(self.name, None)
            query_local_variables_dict.pop(self.x + "_min", None)
            query_local_variables_dict.pop(self.x + "_max", None)


class DateRangeSlider(BaseWidget):
    _datatile_loaded_state: bool = False
    datatile_active_color = DATATILE_ACTIVE_COLOR

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @property
    def x_dtype(self):
        if isinstance(self.source, ColumnDataSource):
            return self.source.data[self.data_x_axis].dtype
        elif isinstance(self.source, (cudf.DataFrame, dask_cudf.DataFrame)):
            return self.source[self.x].dtype
        return None

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = self.datatile_active_color
        else:
            self.chart.bar_color = DATATILE_INACTIVE_COLOR

    def compute_stride(self):
        self.stride = self.stride_type(
            (self.max_value - self.min_value) / self.data_points
        )

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        self.source = dashboard_cls._cuxfilter_df.data
        if self.x_dtype not in CUDF_DATETIME_TYPES:
            raise TypeError(
                "DateRangeSlider: x-column type must be one of "
                + str(CUDF_DATETIME_TYPES)
            )
        self.min_value, self.max_value = get_min_max(
            dashboard_cls._cuxfilter_df.data, self.x
        )
        if self.data_points is None:
            _series = dashboard_cls._cuxfilter_df.data[self.x].value_counts()
            self.data_points = (
                _series.compute().shape[0]
                if isinstance(_series, dask_cudf.core.Series)
                else _series.shape[0]
            )
            del _series
        self.compute_stride()
        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        """
        generate widget range slider
        """
        self.chart = pn.widgets.DateRangeSlider(
            start=self.min_value,
            end=self.max_value,
            value=(self.min_value, self.max_value),
            width=self.width,
            sizing_mode="scale_width",
            **self.params,
        )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        # interactive slider
        self.datatile_active_color = theme.datatile_active_color

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles()
            query_tuple = self._xaxis_np_dt64_transform(event.new)
            dashboard_cls._query_datatiles_by_range(query_tuple)

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if self.chart.value != (self.chart.start, self.chart.end):
            min_temp, max_temp = self.chart.value
            query = f"@{self.x}_min<={self.x}<=@{self.x}_max"
            query_str_dict[self.name] = query
            query_local_variables_dict[self.x + "_min"] = min_temp
            query_local_variables_dict[self.x + "_max"] = max_temp
        else:
            query_str_dict.pop(self.name, None)
            query_local_variables_dict.pop(self.x + "_min", None)
            query_local_variables_dict.pop(self.x + "_max", None)


class IntSlider(BaseWidget):
    _datatile_loaded_state: bool = False
    value = None
    datatile_active_color = DATATILE_ACTIVE_COLOR

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = self.datatile_active_color
        else:
            self.chart.bar_color = DATATILE_INACTIVE_COLOR

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        min, max = get_min_max(dashboard_cls._cuxfilter_df.data, self.x)
        self.min_value = int(min)
        self.max_value = int(max)

        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        """
        generate widget int slider
        """
        if self.value is None:
            self.value = self.min_value
        if self.stride is None:
            self.chart = pn.widgets.IntSlider(
                start=self.min_value,
                end=self.max_value,
                value=self.value,
                step=self.stride,
                width=self.width,
                height=self.height,
                **self.params,
            )
            self.stride = self.chart.step
        else:
            self.chart = pn.widgets.IntSlider(
                start=self.min_value,
                end=self.max_value,
                value=self.value,
                width=self.width,
                height=self.height,
                **self.params,
            )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        # interactive slider
        self.datatile_active_color = theme.datatile_active_color

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles()
            dashboard_cls._query_datatiles_by_indices([], [event.new])

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if len(str(self.chart.value)) > 0:
            query = f"{self.x} == @{self.x}_value"
            query_str_dict[self.name] = query
            query_local_variables_dict[self.x + "_value"] = self.chart.value
        else:
            query_str_dict.pop(self.name, None)
            query_local_variables_dict.pop(self.x + "_value", None)


class FloatSlider(BaseWidget):
    _datatile_loaded_state: bool = False
    value = None
    datatile_active_color = DATATILE_ACTIVE_COLOR

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = self.datatile_active_color
        else:
            self.chart.bar_color = DATATILE_INACTIVE_COLOR

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        self.min_value, self.max_value = get_min_max(
            dashboard_cls._cuxfilter_df.data, self.x
        )
        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        """
        generate widget float slider
        """
        if self.value is None:
            self.value = self.min_value
        if self.stride is None:
            self.chart = pn.widgets.FloatSlider(
                start=self.min_value,
                end=self.max_value,
                value=self.value,
                width=self.width,
                height=self.height,
                **self.params,
            )
            self.stride = self.chart.step
        else:
            self.chart = pn.widgets.FloatSlider(
                start=self.min_value,
                end=self.max_value,
                value=self.value,
                step=self.stride,
                width=self.width,
                height=self.height,
                **self.params,
            )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        # interactive slider
        self.datatile_active_color = theme.datatile_active_color

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)

            dashboard_cls._query_datatiles_by_indices([], [event.new])

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if len(str(self.chart.value)) > 0:
            query = f"{self.x} == @{self.x}_value"
            query_str_dict[self.name] = query
            query_local_variables_dict[self.x + "_value"] = self.chart.value
        else:
            query_str_dict.pop(self.name, None)
            query_local_variables_dict.pop(self.x + "_value", None)


class DropDown(BaseWidget):
    value = None

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        self.min_value, self.max_value = get_min_max(
            dashboard_cls._cuxfilter_df.data, self.x
        )

        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type(1)

        self.calc_list_of_values(dashboard_cls._cuxfilter_df.data)
        self.generate_widget()
        self.add_events(dashboard_cls)

    def calc_list_of_values(self, data):
        """
        calculate unique list of values to be included in the drop down menu
        """
        if self.label_map is None:
            self.list_of_values = data[self.x].unique()
            if isinstance(data, dask_cudf.core.DataFrame):
                self.list_of_values = self.list_of_values.compute()

            self.list_of_values = self.list_of_values.to_pandas().tolist()
            # if len(self.list_of_values) > self.data_points:
            #     self.list_of_values = aggregated_column_unique(self, data)

            if len(self.list_of_values) > 500:
                print(
                    """It is not recommended to use a column with
                    so many different values for dropdown menu"""
                )
            self.list_of_values.append("")
            self.data_points = len(self.list_of_values) - 1
        else:
            self.list_of_values = self.label_map
            self.list_of_values[""] = ""
            self.data_points = len(self.list_of_values.items()) - 1

        self.data_points = len(self.list_of_values) - 1

    def generate_widget(self):
        """
        generate widget dropdown
        """
        self.chart = pn.widgets.Select(
            options=self.list_of_values,
            value="",
            width=self.width,
            height=self.height,
            **self.params,
        )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme

        """
        pass

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices([], [event.new])

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if len(str(self.chart.value)) > 0:
            query = f"{self.x} == @{self.x}_value"
            query_str_dict[self.name] = query
            query_local_variables_dict[self.x + "_value"] = self.chart.value
        else:
            query_str_dict.pop(self.name, None)
            query_local_variables_dict.pop(self.x + "_value", None)


class MultiSelect(BaseWidget):
    value = None

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        self.min_value, self.max_value = get_min_max(
            dashboard_cls._cuxfilter_df.data, self.x
        )

        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type(1)

        self.calc_list_of_values(dashboard_cls._cuxfilter_df.data)

        self.generate_widget()

        self.add_events(dashboard_cls)

    def calc_list_of_values(self, data):
        """
        calculate unique list of values to be included in the multiselect menu
        """
        if self.label_map is None:
            self.list_of_values = data[self.x].unique()
            if isinstance(data, dask_cudf.core.DataFrame):
                self.list_of_values = self.list_of_values.compute()

            self.list_of_values = self.list_of_values.to_pandas().tolist()
            # if len(self.list_of_values) > self.data_points:
            #     self.list_of_values = aggregated_column_unique(self, data)

            if len(self.list_of_values) > 500:
                print(
                    """It is not recommended to use a column with
                    so many different values for multiselect menu"""
                )
            self.list_of_values.append("")
            self.data_points = len(self.list_of_values) - 1
        else:
            self.list_of_values = self.label_map
            self.list_of_values[""] = ""
            self.data_points = len(self.list_of_values.items()) - 1

    def generate_widget(self):
        """
        generate widget multiselect
        """
        self.chart = pn.widgets.MultiSelect(
            options=self.list_of_values,
            value=[""],
            width=self.width,
            height=self.height,
            **self.params,
        )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme

        """
        pass

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices(event.old, event.new)

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if len(self.chart.value) == 0 or self.chart.value == [""]:
            query_str_dict.pop(self.name, None)
        elif len(self.chart.value) == 1:
            query_str_dict[self.name] = f"{self.x}=={self.chart.value[0]}"
        else:
            indices_string = ",".join(map(str, self.chart.value))
            query_str_dict[self.name] = f"{self.x} in ({indices_string})"


class DataSizeIndicator(BaseNumberChart):
    """
    Description:
    """

    css = """
        .indicator {
            text-align: center;
        }
        """
    pn.config.raw_css = pn.config.raw_css + [css]
    title = "Datapoints Selected"

    def get_df_size(self, df):
        if isinstance(df, dask_cudf.DataFrame):
            return df.shape[0].compute()
        return df.shape[0]

    def calculate_source(self, data, patch_update=False):
        """
        calculate source

        Parameters:
        -----------
            data: cudf.DataFrame
            patch_update: bool, default False
        """
        source_dict = {"X": list([1]), "Y": list([self.get_df_size(data)])}

        if patch_update:
            self.chart[0].value = int(source_dict["Y"][0])
            self.chart[1].value = int(
                (self.chart[0].value / self.max_value) * 100
            )
        else:
            self.source = int(source_dict["Y"][0])
            self.source_backup = int(self.source)

    def get_source_y_axis(self):
        """
        get y axis column values
        """
        return self.chart[0].value

    def generate_chart(self):
        """
        generate chart float slider
        """
        self.chart = pn.Column(
            pn.indicators.Number(
                value=int(self.max_value),
                format="{value:,}",
                font_size="18pt",
                sizing_mode="stretch_width",
                css_classes=["indicator"],
            ),
            pn.indicators.Progress(
                name="Progress",
                value=100,
                sizing_mode="stretch_width",
            ),
        )

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the theme
        """
        self.chart[1].bar_color = theme.datasize_indicator_class

    def reset_chart(self, data: int = -1):
        """
        Description:
            if len(data) is 0, reset the chart using self.source_backup
        -------------------------------------------
        Input:
        data = list() --> update self.data_y_axis in self.source
        -------------------------------------------
        """
        if data == -1:
            self.chart[0].value = self.source_backup
        else:
            self.chart[0].value = int(data)
        self.chart[1].value = int((self.chart[0].value / self.max_value) * 100)


class NumberChart(BaseNumberChart):
    """
    Description: Number chart which can be located in either the main
    dashboard or side navbar.
    """

    css = """
        .indicator {
            text-align: center;
        }
        """
    pn.config.raw_css = pn.config.raw_css + [css]

    def calculate_source(self, data, patch_update=False):
        """
        calculate source

        Parameters:
        -----------
            data: cudf.DataFrame
            patch_update: bool, default False
        """
        self.value = getattr(eval(self.expression), self.aggregate_fn)()

        if patch_update:
            self.chart.value = self.value
        else:
            self.source = data
            self.source_backup = self.value

    def get_source_y_axis(self):
        """
        get y axis column values
        """
        return self.chart.value

    def generate_chart(self):
        """
        generate chart float slider
        """

        self.chart = pn.indicators.Number(
            value=int(self.value),
            sizing_mode="stretch_both",
            css_classes=["indicator"],
            format=self.format,
            colors=self.colors,
            font_size=self.font_size,
            **self.library_specific_params,
        )

    def reset_chart(self, data: float = -1):
        """
        Description:
            if len(data) is 0, reset the chart using self.source_backup

        Parameters:
        -----------
            data: float, default -1

        """
        if data == -1:
            self.chart.value = self.source_backup
        else:
            self.chart.value = data


class Card:
    use_data_tiles = False
    _initialized = True
    # widget is a chart type that can be rendered in a sidebar or main layout
    is_widget = True

    @property
    def name(self):
        return f"{self.title}_{self.chart_type}"

    def __init__(self, content="", title="", widget=True):
        self.content = content
        self.title = title
        self.chart_type = "card"

    def view(self):
        return chart_view(self.content, title=self.title)

    def initiate_chart(self, dashboard_cls):
        self.generate_chart()

    def generate_chart(self):
        self.chart = pn.Column(self.content, sizing_mode="stretch_both")
