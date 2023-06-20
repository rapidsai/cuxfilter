from cuxfilter.layouts.chart_views import chart_view
from ..core import BaseWidget
from ..core.aggregate import BaseNumberChart
from ..constants import (
    CUDF_DATETIME_TYPES,
)
from ...assets.cudf_utils import get_min_max
from bokeh.models import ColumnDataSource
import cudf
import dask_cudf
import panel as pn


class RangeSlider(BaseWidget):
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

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            dashboard_cls._reload_charts()

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
    @property
    def x_dtype(self):
        if isinstance(self.source, ColumnDataSource):
            return self.source.data[self.data_x_axis].dtype
        elif isinstance(self.source, (cudf.DataFrame, dask_cudf.DataFrame)):
            return self.source[self.x].dtype
        return None

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

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            dashboard_cls._reload_charts()

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
    value = None

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

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            dashboard_cls._reload_charts()

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
    value = None

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

    def add_events(self, dashboard_cls):
        """
        add events
        """

        def widget_callback(event):
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            dashboard_cls._reload_charts()

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
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            dashboard_cls._reload_charts()

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
            self.compute_query_dict(
                dashboard_cls._query_str_dict,
                dashboard_cls._query_local_variables_dict,
            )
            dashboard_cls._reload_charts()

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

    @property
    def is_datasize_indicator(self):
        return True

    @property
    def name(self):
        return f"{self.chart_type}_{self.title}"

    def get_df_size(self, df):
        if isinstance(df, dask_cudf.DataFrame):
            return df.shape[0].compute()
        return df.shape[0]

    def reload_chart(self, data):
        """
        reload chart
        """
        source_dict = {"X": list([1]), "Y": list([self.get_df_size(data)])}
        self.chart[0].value = int(source_dict["Y"][0])
        self.chart[1].value = int((self.chart[0].value / self.max_value) * 100)

    def generate_chart(self, data):
        """
        generate chart float slider
        """
        self.min_value = 0
        self.max_value = len(data)

        self.chart = pn.Column(
            pn.indicators.Number(
                value=int(self.get_df_size(data)),
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
    expression = ""

    @property
    def name(self):
        return f"{self.expression}_{self.chart_type}_{self.title}"

    def reload_chart(self, data):
        """
        calculate source

        Parameters:
        -----------
            data: cudf.DataFrame
            patch_update: bool, default False
        """
        self.chart.value = getattr(eval(self.expression), self.aggregate_fn)()

    def generate_chart(self, data):
        """
        generate chart float slider
        """
        if "data." not in self.expression:
            # replace column names with {data.column} names to make it work with eval
            for i in data.columns:
                self.expression = self.expression.replace(i, f"data.{i}")

        self.chart = pn.indicators.Number(
            value=int(getattr(eval(self.expression), self.aggregate_fn)()),
            sizing_mode="stretch_both",
            css_classes=["indicator"],
            format=self.format,
            colors=self.colors,
            font_size=self.font_size,
            **self.library_specific_params,
        )


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
