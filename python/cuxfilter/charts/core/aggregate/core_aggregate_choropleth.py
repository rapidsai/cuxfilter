from typing import Dict
import os
import pandas as pd
import numpy as np

from ..core_chart import BaseChart
from ....assets.numba_kernels import calc_groupby
from ....layouts import chart_view
from ....assets import geo_json_mapper


class BaseChoropleth(BaseChart):

    chart_type: str = "choropleth"
    reset_event = None
    _datatile_loaded_state: bool = False
    geo_mapper: Dict[str, str] = {}
    nan_color = "white"
    use_data_tiles = True

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state
        # if self.add_interaction:
        #     if state:
        #         self.filter_widget.bar_color = '#8ab4f7'
        #     else:
        #         self.filter_widget.bar_color = '#d3d9e2'

    def __init__(
        self,
        x,
        color_column,
        elevation_column=None,
        color_aggregate_fn="count",
        color_factor=1,
        elevation_aggregate_fn="sum",
        elevation_factor=1,
        data_points=100,
        add_interaction=True,
        width=800,
        height=400,
        step_size=None,
        step_size_type=int,
        geoJSONSource=None,
        geoJSONProperty=None,
        geo_color_palette=None,
        mapbox_api_key=os.getenv("MAPBOX_API_KEY"),
        map_style="dark",
        tooltip=True,
        **library_specific_params,
    ):
        """
        Description:

        -------------------------------------------
        Input:
            x
            color_column,
            elevation_column,
            color_aggregate_fn,
            color_factor,
            elevation_aggregate_fn,
            elevation_factor,
            geoJSONSource
            geoJSONProperty
            data_points
            add_interaction
            geo_color_palette
            width
            height
            step_size
            step_size_type
            nan_color
            mapbox_api_key
            map_style
            **library_specific_params
        -------------------------------------------

        Ouput:

        """
        self.x = x
        self.color_column = color_column
        self.color_aggregate_fn = color_aggregate_fn
        self.color_factor = color_factor
        self.elevation_column = elevation_column

        self.aggregate_dict = {
            self.color_column: self.color_aggregate_fn,
        }
        if self.elevation_column is not None:
            self.elevation_aggregate_fn = elevation_aggregate_fn
            self.elevation_factor = elevation_factor
            self.aggregate_dict[
                self.elevation_column
            ] = self.elevation_aggregate_fn

        self.data_points = data_points
        self.add_interaction = add_interaction

        if geoJSONSource is None:
            print("geoJSONSource is required for the choropleth map")
        else:
            self.geoJSONSource = geoJSONSource

        self.geo_color_palette = geo_color_palette
        self.geoJSONProperty = geoJSONProperty
        self.geo_mapper, x_range, y_range = geo_json_mapper(
            self.geoJSONSource, self.geoJSONProperty, projection=4326
        )
        self.height = height
        self.width = width

        self.stride = step_size
        self.stride_type = step_size_type
        self.mapbox_api_key = mapbox_api_key
        self.map_style = map_style
        self.library_specific_params = library_specific_params
        self.tooltip = tooltip
        if "x_range" not in self.library_specific_params:
            self.library_specific_params["x_range"] = x_range

        if "y_range" not in self.library_specific_params:
            self.library_specific_params["y_range"] = y_range

        if "nan_color" in self.library_specific_params:
            self.nan_color = self.library_specific_params["nan_color"]
            self.library_specific_params.pop("nan_color")

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        self.min_value = dashboard_cls._data[self.x].min()
        self.max_value = dashboard_cls._data[self.x].max()

        if isinstance(self.geo_mapper, pd.DataFrame):
            self.geo_mapper, x_range, y_range = geo_json_mapper(
                self.geoJSONSource, self.geoJSONProperty, projection=4326
            )
        self.geo_mapper = pd.DataFrame(
            {
                self.x: np.array(list(self.geo_mapper.keys())),
                "coordinates": np.array(list(self.geo_mapper.values())),
            }
        )

        if self.data_points > dashboard_cls._data[self.x].shape[0]:
            self.data_points = dashboard_cls._data[self.x].shape[0]

        if self.stride is None:
            if self.max_value < 1 and self.stride_type == int:
                self.stride_type = float
            if self.stride_type == int:
                self.stride = int(
                    round((self.max_value - self.min_value) / self.data_points)
                )
            else:
                self.stride = float(
                    (self.max_value - self.min_value) / self.data_points
                )

        self.calculate_source(dashboard_cls._data)
        self.generate_chart()
        self.apply_mappers()

        self.add_events(dashboard_cls)

    def view(self):
        return chart_view(self.chart, width=self.width)

    def calculate_source(self, data, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        df = calc_groupby(self, data, agg=self.aggregate_dict)

        dict_temp = {
            self.x: list(df[0].astype(df[0].dtype)),
            self.color_column: list(df[1].astype(df[1].dtype)),
        }
        if self.elevation_column is not None:
            dict_temp[self.elevation_column] = list(df[2].astype(df[2].dtype))

        self.format_source_data(dict_temp, patch_update)

    def get_selection_callback(self, dashboard_cls):
        """
        Description: generate callback for choropleth selection event
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def selection_callback(old, new):
            if dashboard_cls._active_view != self.name:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices(old, new)

        return selection_callback

    def compute_query_dict(self, query_str_dict):
        """
        Description:

        -------------------------------------------
        Input:
        query_dict = reference to dashboard.__cls__.query_dict
        -------------------------------------------

        Ouput:
        """
        list_of_indices = self.get_selected_indices()
        if len(list_of_indices) == 0 or list_of_indices == [""]:
            query_str_dict.pop(self.name, None)
        elif len(list_of_indices) == 1:
            query_str_dict[self.name] = self.x + "==" + str(list_of_indices[0])
        else:
            indices_string = ",".join(map(str, list_of_indices))
            query_str_dict[self.name] = self.x + " in (" + indices_string + ")"

    def add_events(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        if self.add_interaction:
            self.add_selection_event(
                self.get_selection_callback(dashboard_cls)
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

        def reset_callback(event):
            if dashboard_cls._active_view != self.name:
                # reset previous active view and set current chart as
                # active view
                dashboard_cls._reset_current_view(new_active_view=self)
            dashboard_cls._reload_charts()

        # add callback to reset chart button
        self.add_event(self.reset_event, reset_callback)

    def get_selected_indices(self):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        print("function to be overridden by library specific extensions")
        return []

    def add_selection_event(self, callback):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        print("function to be overridden by library specific extensions")

    def query_chart_by_range(self, active_chart, query_tuple, datatile_dict):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: datatile of active chart for
                            current chart[type: pandas df]
        -------------------------------------------

        Ouput:
        """
        for key in datatile_dict:
            datatile = datatile_dict[key]
            datatile_result = None
            min_val, max_val = query_tuple
            datatile_index_min = int(
                round((min_val - active_chart.min_value) / active_chart.stride)
            )
            datatile_index_max = int(
                round((max_val - active_chart.min_value) / active_chart.stride)
            )
            if key == self.color_column:
                temp_agg_function = self.color_aggregate_fn
            else:
                temp_agg_function = self.elevation_aggregate_fn

            if datatile_index_min == 0:

                if temp_agg_function == "mean":
                    datatile_result_sum = np.array(
                        datatile[0].loc[:, datatile_index_max]
                    )
                    datatile_result_count = np.array(
                        datatile[1].loc[:, datatile_index_max]
                    )
                    datatile_result = (
                        datatile_result_sum / datatile_result_count
                    )
                elif temp_agg_function in ["count", "sum", "min", "max"]:
                    datatile_result = datatile.loc[:, datatile_index_max]

            else:
                datatile_index_min -= 1
                if temp_agg_function == "mean":
                    datatile_max0 = datatile[0].loc[:, datatile_index_max]
                    datatile_min0 = datatile[0].loc[:, datatile_index_min]
                    datatile_result_sum = np.array(
                        datatile_max0 - datatile_min0
                    )

                    datatile_max1 = datatile[1].loc[:, datatile_index_max]
                    datatile_min1 = datatile[1].loc[:, datatile_index_min]
                    datatile_result_count = np.array(
                        datatile_max1 - datatile_min1
                    )

                    datatile_result = (
                        datatile_result_sum / datatile_result_count
                    )
                elif temp_agg_function in ["count", "sum", "min", "max"]:
                    datatile_max = datatile.loc[:, datatile_index_max]
                    datatile_min = datatile.loc[:, datatile_index_min]
                    datatile_result = np.array(datatile_max - datatile_min)

            if datatile_result is not None:
                if isinstance(datatile_result, np.ndarray):
                    self.reset_chart(datatile_result, key)
                else:
                    self.reset_chart(np.array(datatile_result), key)

    def query_chart_by_indices_for_mean(
        self,
        active_chart,
        old_indices,
        new_indices,
        datatile,
        calc_new,
        remove_old,
    ):
        """
        Description:

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        """
        if len(new_indices) == 0 or new_indices == [""]:
            datatile_sum_0 = np.array(datatile[0].sum(axis=1, skipna=True))
            datatile_sum_1 = np.array(datatile[1].sum(axis=1, skipna=True))
            datatile_result = datatile_sum_0 / datatile_sum_1
            return datatile_result

        len_y_axis = datatile[0][0][: self.data_points].shape[0]

        datatile_result = np.zeros(shape=(len_y_axis,), dtype=np.float64)
        value_sum = np.zeros(shape=(len_y_axis,), dtype=np.float64)
        value_count = np.zeros(shape=(len_y_axis,), dtype=np.float64)

        for index in new_indices:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            value_sum += np.array(datatile[0][int(index)][: self.data_points])
            value_count += np.array(
                datatile[1][int(index)][: self.data_points]
            )

        datatile_result = value_sum / value_count

        return datatile_result

    def query_chart_by_indices_for_count(
        self,
        active_chart,
        old_indices,
        new_indices,
        datatile,
        calc_new,
        remove_old,
    ):
        """
        Description:

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        """
        if len(new_indices) == 0 or new_indices == [""]:
            datatile_result = np.array(datatile.sum(axis=1, skipna=True))
            return datatile_result

        if len(old_indices) == 0 or old_indices == [""]:
            len_y_axis = datatile[0][: self.data_points].shape[0]
            datatile_result = np.zeros(shape=(len_y_axis,), dtype=np.float64)
        else:
            len_y_axis = datatile[0][: self.data_points].shape[0]
            datatile_result = np.array(
                self.get_source_y_axis(), dtype=np.float64
            )[:len_y_axis]

        for index in calc_new:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            datatile_result += np.array(
                datatile[int(index)][: self.data_points]
            )

        for index in remove_old:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            datatile_result -= np.array(
                datatile[int(index)][: self.data_points]
            )

        return datatile_result

    def query_chart_by_indices(
        self, active_chart, old_indices, new_indices, datatile_dict
    ):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: datatile of active chart for
                        current chart[type: pandas df]
        -------------------------------------------

        Ouput:
        """
        for key in datatile_dict:
            datatile = datatile_dict[key]
            calc_new = list(set(new_indices) - set(old_indices))
            remove_old = list(set(old_indices) - set(new_indices))

            if "" in calc_new:
                calc_new.remove("")
            if "" in remove_old:
                remove_old.remove("")

            if key == self.color_column:
                temp_agg_function = self.color_aggregate_fn
            else:
                temp_agg_function = self.elevation_aggregate_fn

            if temp_agg_function == "mean":
                datatile_result = self.query_chart_by_indices_for_mean(
                    active_chart,
                    old_indices,
                    new_indices,
                    datatile,
                    calc_new,
                    remove_old,
                )
            else:
                datatile_result = self.query_chart_by_indices_for_count(
                    active_chart,
                    old_indices,
                    new_indices,
                    datatile,
                    calc_new,
                    remove_old,
                )
            if isinstance(datatile_result, np.ndarray):
                self.reset_chart(datatile_result, key)
            else:
                self.reset_chart(np.array(datatile_result), key)
