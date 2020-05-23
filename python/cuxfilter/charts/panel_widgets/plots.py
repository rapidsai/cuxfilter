from ..core import BaseWidget
from ..core.aggregate import BaseDataSizeIndicator

import panel as pn
import dask_cudf


class RangeSlider(BaseWidget):
    chart_type: str = "widget_range_slider"
    _datatile_loaded_state: bool = False
    datatile_active_color = "#8ab4f7"

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = self.datatile_active_color
        else:
            self.chart.bar_color = "#d3d9e2"

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        if type(dashboard_cls._data) == dask_cudf.core.DataFrame:
            self.min_value = dashboard_cls._data[self.x].min().compute()
            self.max_value = dashboard_cls._data[self.x].max().compute()
        else:
            self.min_value = dashboard_cls._data[self.x].min()
            self.max_value = dashboard_cls._data[self.x].max()

        if self.max_value < 1 and self.stride_type == int:
            self.stride_type = float

        self.generate_widget()
        self.add_events(dashboard_cls)

    def generate_widget(self):
        """
        generate widget range slider
        """
        if self.stride is None:
            self.chart = pn.widgets.RangeSlider(
                name=self.x,
                start=self.min_value,
                end=self.max_value,
                value=(self.min_value, self.max_value),
                **self.params,
            )
            self.stride = self.chart.step
        else:
            self.chart = pn.widgets.RangeSlider(
                name=self.x,
                start=self.min_value,
                end=self.max_value,
                value=(self.min_value, self.max_value),
                step=self.stride,
                **self.params,
            )

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        # interactive slider
        self.datatile_active_color = properties_dict["widgets"][
            "datatile_active_color"
        ]

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles()

            dashboard_cls._query_datatiles_by_range(event.new)

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if self.chart.value != (self.chart.start, self.chart.end):
            min_temp, max_temp = self.chart.value
            query_str_dict[self.name] = (
                str(self.stride_type(round(min_temp, 4)))
                + "<="
                + str(self.x)
                + "<="
                + str(self.stride_type(round(max_temp, 4)))
            )
        else:
            query_str_dict.pop(self.name, None)


class IntSlider(BaseWidget):
    chart_type: str = "widget_int_slider"
    _datatile_loaded_state: bool = False
    value = None
    datatile_active_color = "#8ab4f7"

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = self.datatile_active_color
        else:
            self.chart.bar_color = "#d3d9e2"

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        if type(dashboard_cls._data) == dask_cudf.core.DataFrame:
            self.min_value = int(dashboard_cls._data[self.x].min().compute())
            self.max_value = int(dashboard_cls._data[self.x].max().compute())
        else:
            self.min_value = int(dashboard_cls._data[self.x].min())
            self.max_value = int(dashboard_cls._data[self.x].max())

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
                name=self.x,
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
                name=self.x,
                start=self.min_value,
                end=self.max_value,
                value=self.value,
                width=self.width,
                height=self.height,
                **self.params,
            )

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        # interactive slider
        self.datatile_active_color = properties_dict["widgets"][
            "datatile_active_color"
        ]

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices([], [event.new])

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if len(str(self.chart.value)) > 0:
            query_str_dict[self.name] = (
                str(self.x) + "==" + str(self.chart.value)
            )
        else:
            query_str_dict.pop(self.name, None)


class FloatSlider(BaseWidget):
    chart_type: str = "widget_float_slider"
    _datatile_loaded_state: bool = False
    value = None
    datatile_active_color = "#8ab4f7"

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        if state:
            self.chart.bar_color = self.datatile_active_color
        else:
            self.chart.bar_color = "#d3d9e2"

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        if type(dashboard_cls._data) == dask_cudf.core.DataFrame:
            self.min_value = dashboard_cls._data[self.x].min().compute()
            self.max_value = dashboard_cls._data[self.x].max().compute()
        else:
            self.min_value = dashboard_cls._data[self.x].min()
            self.max_value = dashboard_cls._data[self.x].max()
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
                name=self.x,
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
                name=self.x,
                start=self.min_value,
                end=self.max_value,
                value=self.value,
                step=self.stride,
                width=self.width,
                height=self.height,
                **self.params,
            )

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        # interactive slider
        self.datatile_active_color = properties_dict["widgets"][
            "datatile_active_color"
        ]

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)

            dashboard_cls._query_datatiles_by_indices([], [event.new])

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if len(str(self.chart.value)) > 0:
            query_str_dict[self.name] = (
                str(self.x) + "==" + str(self.chart.value)
            )
        else:
            query_str_dict.pop(self.name, None)


class DropDown(BaseWidget):
    chart_type: str = "widget_dropdown"
    value = None

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        if type(dashboard_cls._data) == dask_cudf.core.DataFrame:
            self.min_value = dashboard_cls._data[self.x].min().compute()
            self.max_value = dashboard_cls._data[self.x].max().compute()
        else:
            self.min_value = dashboard_cls._data[self.x].min()
            self.max_value = dashboard_cls._data[self.x].max()

        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type(1)

        self.calc_list_of_values(dashboard_cls._data)
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
            name=self.x,
            options=self.list_of_values,
            value="",
            width=self.width,
            height=self.height,
            **self.params,
        )

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        css = """
            .custom-dropdown select, .custom-dropdown option {{
                background-color: {0} !important;
            }}
            """
        css = css.format(properties_dict["widgets"]["background_color"])
        pn.config.raw_css = pn.config.raw_css + [css]

        self.chart.css_classes = ["custom-dropdown"]

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices([], [event.new])

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict):
        """
        compute query value

        Parameters:
        -----------

        query_dict:
            reference to dashboard.__cls__.query_dict
        """
        if len(str(self.chart.value)) > 0:
            query_str_dict[self.name] = (
                str(self.x) + "==" + str(self.chart.value)
            )
        else:
            query_str_dict.pop(self.name, None)


class MultiSelect(BaseWidget):
    chart_type: str = "widget_multi_select"
    value = None

    def initiate_chart(self, dashboard_cls):
        """
        initiate chart on dashboard creation
        """
        if type(dashboard_cls._data) == dask_cudf.core.DataFrame:
            self.min_value = dashboard_cls._data[self.x].min().compute()
            self.max_value = dashboard_cls._data[self.x].max().compute()
        else:
            self.min_value = dashboard_cls._data[self.x].min()
            self.max_value = dashboard_cls._data[self.x].max()

        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            self.stride = self.stride_type(1)

        self.calc_list_of_values(dashboard_cls._data)

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
            name=self.x,
            options=self.list_of_values,
            value=[""],
            width=self.width,
            height=self.height,
            **self.params,
        )

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        css = """
            .custom-dropdown select, .custom-dropdown option {{
                background-color: {0} !important;

            }}
            .custom-dropdown {{
                font-size: 15px !important;
                margin-bottom: 5px;
            }}
            """
        css = css.format(properties_dict["widgets"]["background_color"])
        pn.config.raw_css = pn.config.raw_css + [css]

        self.chart.css_classes = ["custom-dropdown"]

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices(event.old, event.new)

        # add callback to filter_Widget on value change
        self.chart.param.watch(widget_callback, ["value"], onlychanged=False)
        # self.add_reset_event(dashboard_cls)

    def compute_query_dict(self, query_str_dict):
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
            query_str_dict[self.name] = (
                self.x + "==" + str(self.chart.value[0])
            )
        else:
            indices_string = ",".join(map(str, self.chart.value))
            query_str_dict[self.name] = self.x + " in (" + indices_string + ")"


class DataSizeIndicator(BaseDataSizeIndicator):
    """
        Description:
    """

    css = """
        .non-handle-temp .bk-noUi-origin {
        visibility: hidden;
        color:blue;
        }

        .non-handle-temp [disabled] .bk-noUi-connect {
            background: purple;
        }
        """
    pn.config.raw_css = pn.config.raw_css + [css]

    def format_source_data(self, source_dict, patch_update=False):
        """
        format source

        Parameters:
        -----------
        source_dict: {'X': [],'Y': []}

        """
        if patch_update:
            self.chart.value = float(source_dict["Y"][0])
        else:
            self.source = float(source_dict["Y"][0])
            self.source_backup = self.source

    def get_source_y_axis(self):
        """
        get y axis column values
        """
        return self.chart.value

    def generate_chart(self):
        """
        generate chart float slider
        """
        self.chart = pn.widgets.FloatSlider(
            name="Data Points selected",
            width=self.width,
            start=0,
            end=self.max_value,
            value=self.max_value,
        )

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.
        """

        self.chart.bar_color = properties_dict["data_size_indicator_color"]

    def reload_chart(self, data, patch_update=True):
        """
        reload chart
        """
        self.calculate_source(data, patch_update=patch_update)

    def reset_chart(self, data: float = -1):
        """
        Description:
            if len(data) is 0, reset the chart using self.source_backup
        -------------------------------------------
        Input:
        data = list() --> update self.data_y_axis in self.source
        -------------------------------------------

        Ouput:
        """
        if data == -1:
            self.chart.value = self.source_backup
        else:
            self.chart.value = float(data)
