from typing import Dict
import os
import numpy as np

from ..core_chart import BaseChart
from ....assets.numba_kernels import calc_groupby
from ....assets import geo_json_mapper
from ....layouts import chart_view
from ....assets.cudf_utils import get_min_max
from ...constants import CUXF_NAN_COLOR

np.seterr(divide="ignore", invalid="ignore")


class BaseChoropleth(BaseChart):
    reset_event = None
    _datatile_loaded_state: bool = False
    geo_mapper: Dict[str, str] = {}
    use_data_tiles = True

    @property
    def datatile_loaded_state(self):
        return self._datatile_loaded_state

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

    @datatile_loaded_state.setter
    def datatile_loaded_state(self, state: bool):
        self._datatile_loaded_state = state

    def __init__(
        self,
        x,
        color_column,
        elevation_column=None,
        color_aggregate_fn="count",
        color_factor=1,
        elevation_aggregate_fn="sum",
        elevation_factor=1,
        add_interaction=True,
        width=800,
        height=400,
        geoJSONSource=None,
        geoJSONProperty=None,
        geo_color_palette=None,
        mapbox_api_key=os.getenv("MAPBOX_API_KEY"),
        map_style=None,
        tooltip=True,
        tooltip_include_cols=[],
        nan_color=CUXF_NAN_COLOR,
        title="",
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
            add_interaction
            geo_color_palette
            width
            height
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

        self.add_interaction = add_interaction

        if geoJSONSource is None:
            print("geoJSONSource is required for the choropleth map")
        else:
            self.geoJSONSource = geoJSONSource

        self.geo_color_palette = geo_color_palette
        self.geoJSONProperty = geoJSONProperty
        _, x_range, y_range = geo_json_mapper(
            self.geoJSONSource, self.geoJSONProperty, projection=4326
        )
        self.height = height
        self.width = width
        self.stride = 1
        self.mapbox_api_key = mapbox_api_key
        self.map_style = map_style
        self.library_specific_params = library_specific_params
        self.tooltip = tooltip
        self.tooltip_include_cols = tooltip_include_cols
        self.nan_color = nan_color
        self.title = title or f"{self.x}"
        if "x_range" not in self.library_specific_params:
            self.library_specific_params["x_range"] = x_range

        if "y_range" not in self.library_specific_params:
            self.library_specific_params["y_range"] = y_range

    def initiate_chart(self, dashboard_cls):
        """
        Description:

        -------------------------------------------
        Input:
        data: cudf DataFrame
        -------------------------------------------

        Ouput:

        """
        self.min_value, self.max_value = get_min_max(
            dashboard_cls._cuxfilter_df.data, self.x
        )

        self.geo_mapper, x_range, y_range = geo_json_mapper(
            self.geoJSONSource,
            self.geoJSONProperty,
            4326,
            self.x,
            dashboard_cls._cuxfilter_df.data[self.x].dtype,
        )

        self.calculate_source(dashboard_cls._cuxfilter_df.data)
        self.generate_chart()
        self.apply_mappers()

        self.add_events(dashboard_cls)

    def view(self):
        return chart_view(
            self.chart.view(), width=self.width, title=self.title
        )

    def calculate_source(self, data, patch_update=False):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        self.format_source_data(
            calc_groupby(self, data, agg=self.aggregate_dict), patch_update
        )

    def get_selection_callback(self, dashboard_cls):
        """
        Description: generate callback for choropleth selection event
        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """

        def selection_callback(old, new):
            if dashboard_cls._active_view != self:
                dashboard_cls._reset_current_view(new_active_view=self)
                dashboard_cls._calc_data_tiles(cumsum=False)
            dashboard_cls._query_datatiles_by_indices(old, new)

        return selection_callback

    def compute_query_dict(self, query_str_dict, query_local_variables_dict):
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
            query_str_dict[self.name] = f"{self.x}=={list_of_indices[0]}"
        else:
            indices_string = ",".join(map(str, list_of_indices))
            query_str_dict[self.name] = f"{self.x} in ({indices_string})"

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
            if dashboard_cls._active_view != self:
                # reset previous active view and set current chart as
                # active view
                dashboard_cls._reset_current_view(new_active_view=self)
            dashboard_cls._reload_charts()

        # add callback to reset chart button
        self.chart.on_event(self.reset_event, reset_callback)

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

    def query_chart_by_range(self, active_chart, query_tuple, datatile):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: dict, datatile of active chart for
                            current chart[type: pandas df]
        -------------------------------------------

        Ouput:
        """
        if type(datatile) != dict:
            # choropleth datatile should be a dictionary
            datatile = {self.color_column: datatile}
        for key in datatile:
            datatile_result = None
            min_val, max_val = query_tuple
            datatile_index_min = int(
                round((min_val - active_chart.min_value) / active_chart.stride)
            )
            datatile_index_max = int(
                round((max_val - active_chart.min_value) / active_chart.stride)
            )
            datatile_indices = (
                (self.source[self.x] - self.min_value) / self.stride
            ).astype(int)

            if key == self.color_column:
                temp_agg_function = self.color_aggregate_fn
            elif self.elevation_column is not None:
                temp_agg_function = self.elevation_aggregate_fn

            if datatile_index_min == 0:

                if temp_agg_function == "mean":
                    datatile_result_sum = np.array(
                        datatile[key][0].loc[
                            datatile_indices, datatile_index_max
                        ]
                    )
                    datatile_result_count = np.array(
                        datatile[key][1].loc[
                            datatile_indices, datatile_index_max
                        ]
                    )
                    datatile_result = (
                        datatile_result_sum / datatile_result_count
                    )
                elif temp_agg_function in ["count", "sum"]:
                    datatile_result = datatile[key].loc[
                        datatile_indices, datatile_index_max
                    ]
                elif temp_agg_function in ["min", "max"]:
                    datatile_result = np.array(
                        getattr(
                            datatile[key].loc[datatile_indices, 1:],
                            temp_agg_function,
                        )(axis=1, skipna=True)
                    )
            else:
                datatile_index_min -= 1
                if temp_agg_function == "mean":
                    datatile_max0 = datatile[key][0].loc[
                        datatile_indices, datatile_index_max
                    ]
                    datatile_min0 = datatile[key][0].loc[
                        datatile_indices, datatile_index_min
                    ]
                    datatile_result_sum = np.array(
                        datatile_max0 - datatile_min0
                    )

                    datatile_max1 = datatile[key][1].loc[
                        datatile_indices, datatile_index_max
                    ]
                    datatile_min1 = datatile[key][1].loc[
                        datatile_indices, datatile_index_min
                    ]
                    datatile_result_count = np.array(
                        datatile_max1 - datatile_min1
                    )

                    datatile_result = (
                        datatile_result_sum / datatile_result_count
                    )
                elif temp_agg_function in ["count", "sum"]:
                    datatile_max = datatile[key].loc[
                        datatile_indices, datatile_index_max
                    ]
                    datatile_min = datatile[key].loc[
                        datatile_indices, datatile_index_min
                    ]
                    datatile_result = np.array(datatile_max - datatile_min)
                elif temp_agg_function in ["min", "max"]:
                    datatile_result = np.array(
                        getattr(
                            datatile[key].loc[
                                datatile_indices,
                                datatile_index_min:datatile_index_max,
                            ],
                            temp_agg_function,
                        )(axis=1, skipna=True)
                    )

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
        datatile_indices = (
            (self.source[self.x] - self.min_value) / self.stride
        ).astype(int)
        if len(new_indices) == 0 or new_indices == [""]:
            datatile_sum_0 = np.array(
                datatile[0].loc[datatile_indices].sum(axis=1, skipna=True)
            )
            datatile_sum_1 = np.array(
                datatile[1].loc[datatile_indices].sum(axis=1, skipna=True)
            )
            datatile_result = datatile_sum_0 / datatile_sum_1
            return datatile_result

        len_y_axis = datatile[0][0].loc[datatile_indices].shape[0]

        datatile_result = np.zeros(shape=(len_y_axis,), dtype=np.float64)
        value_sum = np.zeros(shape=(len_y_axis,), dtype=np.float64)
        value_count = np.zeros(shape=(len_y_axis,), dtype=np.float64)

        for index in new_indices:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            value_sum += np.array(
                datatile[0][int(index)].loc[datatile_indices]
            )
            value_count += np.array(
                datatile[1][int(index)].loc[datatile_indices]
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
        key,
    ):
        """
        Description:

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        """
        datatile_indices = (
            (self.source[self.x] - self.min_value) / self.stride
        ).astype(int)
        if len(new_indices) == 0 or new_indices == [""]:
            datatile_result = np.array(
                datatile.loc[datatile_indices, :].sum(axis=1, skipna=True)
            )
            return datatile_result

        if len(old_indices) == 0 or old_indices == [""]:
            len_y_axis = datatile[0].loc[datatile_indices].shape[0]
            datatile_result = np.zeros(shape=(len_y_axis,), dtype=np.float64)
        else:
            len_y_axis = datatile[0].loc[datatile_indices].shape[0]
            datatile_result = np.array(self.source[key], dtype=np.float64)[
                :len_y_axis
            ]

        for index in calc_new:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            datatile_result += np.array(
                datatile.loc[datatile_indices, int(index)]
            )

        for index in remove_old:
            index = int(
                round((index - active_chart.min_value) / active_chart.stride)
            )
            datatile_result -= np.array(
                datatile.loc[datatile_indices, int(index)]
            )
        return datatile_result

    def query_chart_by_indices_for_minmax(
        self,
        active_chart,
        old_indices,
        new_indices,
        datatile,
        temp_agg_function,
    ):
        """
        Description:

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        """
        datatile_indices = (
            (self.source[self.x] - self.min_value) / self.stride
        ).astype(int)

        if len(new_indices) == 0 or new_indices == [""]:
            # get min or max from datatile df, skipping column 0(always 0)
            datatile_result = np.array(
                getattr(datatile.loc[datatile_indices, 1:], temp_agg_function)(
                    axis=1, skipna=True
                )
            )
        else:
            new_indices = np.array(new_indices)
            new_indices = np.round(
                (new_indices - active_chart.min_value) / active_chart.stride
            ).astype(int)
            datatile_result = np.array(
                getattr(
                    datatile.loc[datatile_indices, list(new_indices)],
                    temp_agg_function,
                )(axis=1, skipna=True)
            )

        return datatile_result

    def query_chart_by_indices(
        self, active_chart, old_indices, new_indices, datatile
    ):
        """
        Description:

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. old_indices: list
            3. new_indices: list
            4. datatile: dict, datatile of active chart for
                        current chart[type: pandas df]
        -------------------------------------------

        Ouput:
        """
        if type(datatile) != dict:
            # choropleth datatile should be a dictionary
            datatile = {self.color_column: datatile}
        for key in datatile:
            calc_new = list(set(new_indices) - set(old_indices))
            remove_old = list(set(old_indices) - set(new_indices))

            if "" in calc_new:
                calc_new.remove("")
            if "" in remove_old:
                remove_old.remove("")

            if key == self.color_column:
                temp_agg_function = self.color_aggregate_fn
            elif self.elevation_column is not None:
                temp_agg_function = self.elevation_aggregate_fn

            if temp_agg_function == "mean":
                datatile_result = self.query_chart_by_indices_for_mean(
                    active_chart,
                    old_indices,
                    new_indices,
                    datatile[key],
                    calc_new,
                    remove_old,
                )
            elif temp_agg_function in ["count", "sum"]:
                datatile_result = self.query_chart_by_indices_for_count(
                    active_chart,
                    old_indices,
                    new_indices,
                    datatile[key],
                    calc_new,
                    remove_old,
                    key,
                )
            elif temp_agg_function in ["min", "max"]:
                datatile_result = self.query_chart_by_indices_for_minmax(
                    active_chart,
                    old_indices,
                    new_indices,
                    datatile[key],
                    temp_agg_function,
                )
            if isinstance(datatile_result, np.ndarray):
                self.reset_chart(datatile_result, key)
            else:
                self.reset_chart(np.array(datatile_result), key)
