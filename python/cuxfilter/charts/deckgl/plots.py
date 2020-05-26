from ..core.aggregate import BaseChoropleth
from .bindings import PolygonDeckGL

import pandas as pd
import numpy as np
from typing import Type
from bokeh.models import ColumnDataSource, LinearColorMapper
import bokeh


class Choropleth(BaseChoropleth):

    # reset event handling not required, as the default behavior
    # unselects all selected points, and that is already taken care of
    reset_event = None
    coordinates = "coordinates"
    source: Type[ColumnDataSource]

    layer_spec = {
        "opacity": 1,
        "getLineWidth": 10,
        "getPolygon": "@@=coordinates",
        "getElevation": "",
        "getFillColor": "@@=__color__",
        "stroked": True,
        "filled": True,
        "extruded": True,
        "lineWidthScale": 10,
        "lineWidthMinPixels": 1,
        "highlightColor": [200, 200, 200, 200],
        "visible": True,
        "pickable": True,
        "getLineColor": [0, 188, 212],
        "autoHighlight": True,
        "elevationScale": 0.8,
        "pickMultipleObjects": True,
    }

    deck_spec = {
        "mapboxApiAccessToken": "",
        "mapStyle": "",
        "initialViewState": {
            "latitude": 38.212288,
            "longitude": -107.101581,
            "zoom": 3,
            "max_zoom": 16,
        },
        "controller": True,
    }

    def format_source_data(self, source_dict, patch_update=False):
        """
        format source

        Parameters:
        -----------
        source_dict: {'X': [], 'Y': []}

        ColumnDataSource: {
            'X': np.array(list),
            'Y': np.array(list)
        }
        """
        res_df = pd.DataFrame(source_dict)
        if patch_update is False:
            result_df = res_df.merge(self.geo_mapper, on=self.x, how="left")
            result_df["index"] = result_df.index
            result_df = result_df.dropna(subset=["coordinates"])

            self.source_backup = result_df

            result_np = result_df.values
            result_dict = {}

            for i in range(result_np.shape[1]):
                result_dict[result_df.columns[i]] = result_np[:, i]

            if self.source is None:
                self.source = ColumnDataSource(result_dict)
            else:
                self.source.stream(result_dict)

        else:
            result_df = res_df.merge(self.geo_mapper, on=self.x, how="left")
            result_df["index"] = result_df.index

            result_df = result_df.dropna(subset=["coordinates"])

            result_np = result_df.values

            result_dict = {}

            for i in range(result_np.shape[1]):
                result_dict[result_df.columns[i]] = [
                    (slice(result_np[:, i].size), result_np[:, i])
                ]

            self.source.patch(result_dict)

    def get_mean(self, x):
        return (x[0] + x[1]) / 2

    def generate_chart(self):
        """
        generate chart
        """
        if self.geo_color_palette is None:
            mapper = LinearColorMapper(
                palette=bokeh.palettes.Purples9,
                nan_color=self.nan_color,
                low=np.nanmin(self.source.data[self.color_column]),
                high=np.nanmax(self.source.data[self.color_column]),
                name=self.color_column,
            )
        else:
            mapper = LinearColorMapper(
                palette=self.geo_color_palette,
                nan_color=self.nan_color,
                low=np.nanmin(self.source.data[self.color_column]),
                high=np.nanmax(self.source.data[self.color_column]),
                name=self.color_column,
            )
        if "opacity" in self.library_specific_params:
            self.layer_spec["opacity"] = self.library_specific_params[
                "opacity"
            ]

        if self.elevation_column is not None:
            self.layer_spec["getElevation"] = "@@={}*{}".format(
                self.elevation_column, self.elevation_factor
            )

        self.deck_spec["initialViewState"]["latitude"] = self.get_mean(
            self.library_specific_params["y_range"]
        )
        self.deck_spec["initialViewState"]["longitude"] = self.get_mean(
            self.library_specific_params["x_range"]
        )
        self.deck_spec["mapboxApiAccessToken"] = self.mapbox_api_key
        self.deck_spec["mapStyle"] = "mapbox://styles/mapbox/{}-v9".format(
            self.map_style
        )

        self.chart = PolygonDeckGL(
            x=self.x,
            layer_spec=self.layer_spec,
            deck_spec=self.deck_spec,
            color_mapper=mapper,
            data_source=self.source,
            width=self.width,
            height=self.height,
            tooltip=self.tooltip,
        )

    def update_dimensions(self, width=None, height=None):
        """
        update dimensions
        """
        if width is not None:
            self.chart.width = width
        if height is not None:
            self.chart.height = height

    # def apply_mappers(self):
    #     """
    #     apply dict mappers to x and y axes if provided
    #     ---
    #     """
    #     if self.x_label_map is not None:
    #         self.chart.xaxis.major_label_overrides = self.x_label_map
    #     if self.y_label_map is not None:
    #         self.chart.yaxis.major_label_overrides = self.y_label_map

    def reload_chart(self, data, patch_update=True):
        """
        reload chart
        ---
        """
        self.calculate_source(data, patch_update=patch_update)

    def reset_chart(self, data: np.array = np.array([]), column=None):
        """
        if len(data) is 0, reset the chart using self.source_backup

        Parameters:
        -----------
        data:  list()
            update self.data_y_axis in self.source
        """
        if column is None:
            self.format_source_data(
                self.source_backup.to_dict(orient="list"), patch_update=True
            )
        else:
            x_axis_len = self.source.data[self.x].size
            data = data[:x_axis_len]

            patch_dict = {column: [(slice(data.size), data)]}
            self.source.patch(patch_dict)

    def map_indices_to_values(self, indices: list):
        """
        map index values to column values
        ---
        """
        list_final = []
        for n in indices:
            list_final.append(int(self.source.data[self.x][n]))
        return list_final

    def get_selected_indices(self):
        """
        get list of selected indices
        ---
        """
        return self.map_indices_to_values(self.source.selected.indices)

    def add_selection_event(self, callback):
        """
        add selection event
        ---
        """

        def temp_callback(attr, old, new):
            old = self.map_indices_to_values(old)
            new = self.map_indices_to_values(new)
            callback(old, new)

        self.source.selected.on_change("indices", temp_callback)

    def apply_theme(self, properties_dict):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        if self.geo_color_palette is None:
            mapper = LinearColorMapper(
                palette=properties_dict["chart_color"]["color_palette"],
                nan_color=self.nan_color,
                low=np.nanmin(self.source.data[self.color_column]),
                high=np.nanmax(self.source.data[self.color_column]),
                name=self.color_column,
            )
            self.chart.color_mapper = mapper
