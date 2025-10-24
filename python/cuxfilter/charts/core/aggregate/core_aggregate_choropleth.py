# SPDX-FileCopyrightText: Copyright (c) 2019-2025, NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from typing import Dict
import os
import numpy as np
import panel as pn

from ..core_chart import BaseChart
from ....assets.numba_kernels import calc_groupby
from ....assets import geo_json_mapper
from ....assets.cudf_utils import get_min_max
from ...constants import CUXF_NAN_COLOR

np.seterr(divide="ignore", invalid="ignore")


class BaseChoropleth(BaseChart):
    reset_event = None
    geo_mapper: Dict[str, str] = {}
    use_data_tiles = True
    source = None

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
        geoJSONSource=None,
        geoJSONProperty=None,
        geo_color_palette=None,
        mapbox_api_key=os.getenv("MAPBOX_API_KEY"),
        map_style=None,
        tooltip=True,
        tooltip_include_cols=[],
        nan_color=CUXF_NAN_COLOR,
        title="",
        x_range=None,
        y_range=None,
        opacity=None,
        layer_spec={},  # deck.gl layer spec
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
            self.aggregate_dict[self.elevation_column] = (
                self.elevation_aggregate_fn
            )

        self.add_interaction = add_interaction

        if geoJSONSource is None:
            print("geoJSONSource is required for the choropleth map")
        else:
            self.geoJSONSource = geoJSONSource

        self.geo_color_palette = geo_color_palette
        self.geoJSONProperty = geoJSONProperty
        if not (x_range and y_range):
            # get default x_range and y_range from geoJSONSource
            default_x_range, default_y_range = geo_json_mapper(
                self.geoJSONSource, self.geoJSONProperty, projection=4326
            )[1:]
            x_range = x_range or default_x_range
            y_range = y_range or default_y_range
        self.x_range = x_range
        self.y_range = y_range
        self.stride = 1
        self.mapbox_api_key = mapbox_api_key
        self.map_style = map_style
        self.tooltip = tooltip
        self.tooltip_include_cols = tooltip_include_cols
        self.nan_color = nan_color
        self.title = title or f"{self.x}"
        self.opacity = opacity
        self.input_layer_spec = layer_spec

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

    def view(self, width=800, height=400):
        return pn.WidgetBox(self.chart.pane, width=width, height=height)

    def get_dashboard_view(self):
        return pn.panel(self.chart.view(), sizing_mode="stretch_both")

    def calculate_source(self, data):
        """
        Description:

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        """
        self.format_source_data(
            calc_groupby(self, data, agg=self.aggregate_dict)
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
            self.compute_query_dict(dashboard_cls._query_str_dict)
            if old != new and not new:
                dashboard_cls._reload_charts()
            else:
                dashboard_cls._reload_charts(ignore_cols=[self.name])

        return selection_callback

    def compute_query_dict(self, query_str_dict):
        """
        Description:

        -------------------------------------------
        Input:
        query_str_dict = reference to dashboard.__cls__.query_str_dict
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
            dashboard_cls._query_str_dict.pop(self.name, None)
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
