from ..core.aggregate import BaseChoropleth
from .bindings import PanelDeck

import pandas as pd
import numpy as np
from typing import Type
from bokeh.models import ColumnDataSource
import bokeh
from PIL import ImageColor


class Choropleth(BaseChoropleth):

    debug = False
    # reset event handling not required, as the default behavior
    # unselects all selected points, and that is already taken care of
    reset_event = None
    no_colors_set = False
    coordinates = "coordinates"
    source: Type[ColumnDataSource]
    rgba_columns: Type[list] = ["__r__", "__g__", "__b__", "__a__"]
    # rgba_columns = "__rgba__"
    layer_spec = {
        "@@type": "PolygonLayer",
        "opacity": 1,
        "getLineWidth": 10,
        "getPolygon": "@@=coordinates",
        "getFillColor": "@@=[__r__, __g__, __b__, __a__]",
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
        "mapStyle": "",
        "initialViewState": {
            "latitude": 38.212288,
            "longitude": -107.101581,
            "zoom": 3,
            "max_zoom": 16,
        },
        "controller": True,
    }

    def compute_colors(self):
        if self.geo_color_palette is None:
            self.no_colors_set = True
            self.geo_color_palette = bokeh.palettes.Purples9

        min, max = (
            self.source[self.color_column].min(skipna=True),
            self.source[self.color_column].max(skipna=True),
        )

        # set default nan_color
        self.source[self.rgba_columns] = list(
            ImageColor.getrgb(self.nan_color)
        ) + [50]
        if min == max:
            default_color = list(
                ImageColor.getrgb(self.geo_color_palette[0])
            ) + [255]
            color_ids = self.source[self.color_column] == min
            self.source.loc[color_ids, self.rgba_columns] = default_color
        elif not all(np.isnan([min, max])):
            BREAKS = np.linspace(
                min,
                max,
                len(self.geo_color_palette),
            )
            color_map = {
                **{
                    key: list(ImageColor.getrgb(val)) + [255]
                    for key, val in enumerate(self.geo_color_palette)
                },
                np.nan: list(ImageColor.getrgb(self.nan_color)) + [50],
            }

            idx = self.source.index
            if self.chart:
                # set base colors for current state if chart exists
                inds = pd.cut(
                    self.source[self.color_column],
                    BREAKS,
                    labels=False,
                    include_lowest=True,
                )
                self.chart.colors.loc[:, self.rgba_columns] = inds.map(
                    color_map
                ).tolist()
                if len(self.chart.indices) > 0:
                    # highlight selected indices only
                    idx = self.chart.indices.intersection(idx)

            inds = pd.cut(
                self.source.loc[idx, self.color_column],
                BREAKS,
                labels=False,
                include_lowest=True,
            )
            self.source.loc[idx, self.rgba_columns] = inds.map(
                color_map
            ).tolist()

    def format_source_data(self, data, patch_update=False):
        """
        format source

        Parameters:
        -----------
        data: cudf.DataFrame or dask_cudf.DataFrame
        patch_update: boolean

        returns a pandas.DataFrame merged with geojson polygon coordinates
        """
        source_temp = (
            data.to_pandas()
            .merge(self.geo_mapper, on=self.x, how="left")
            .dropna(subset=["coordinates"])
            .reset_index(drop=True)
        )
        if patch_update is False:
            self.source = source_temp
            self.compute_colors()
        else:
            self.source.loc[
                :, [self.color_column, self.elevation_column]
            ] = np.nan
            self.source.loc[
                self.source[self.x].isin(source_temp[self.x]),
                [self.color_column, self.elevation_column],
            ] = source_temp[[self.color_column, self.elevation_column]].values
            self.compute_colors()

        if self.chart:
            self.chart.data = self.source

    def get_mean(self, x):
        return (x[0] + x[1]) / 2

    def generate_chart(self):
        """
        generate chart
        """

        self.layer_spec["id"] = f"PolygonLayer-{self.name}"

        if "opacity" in self.library_specific_params:
            self.layer_spec["opacity"] = self.library_specific_params[
                "opacity"
            ]

        if self.elevation_column is not None:
            self.layer_spec[
                "getElevation"
            ] = f"@@={self.elevation_column}*{self.elevation_factor}"

        self.deck_spec["initialViewState"]["latitude"] = self.get_mean(
            self.library_specific_params["y_range"]
        )
        self.deck_spec["initialViewState"]["longitude"] = self.get_mean(
            self.library_specific_params["x_range"]
        )
        if self.mapbox_api_key:
            self.deck_spec["mapboxApiAccessToken"] = self.mapbox_api_key
        self.deck_spec["mapStyle"] = self.map_style

        self.deck_spec["layers"] = [self.layer_spec]

        self.chart = PanelDeck(
            x=self.x,
            data=self.source,
            spec=self.deck_spec,
            colors=self.source[self.rgba_columns],
            width=self.width,
            height=self.height,
            default_color=list(ImageColor.getrgb(self.nan_color)) + [50],
            tooltip_include_cols=self.tooltip_include_cols,
        )

    def update_dimensions(self, width=None, height=None):
        """
        update dimensions
        """
        if width is not None:
            self.chart.width = width
        if height is not None:
            self.chart.height = height

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
        if column is not None:
            self.source[column] = data
            if column == self.color_column:
                self.compute_colors()
            self.chart.data = self.source

    def map_indices_to_values(self, indices: list):
        """
        map index values to column values
        ---
        """
        list_final = []
        for n in indices:
            list_final.append(int(self.source[self.x][n]))
        return list_final

    def get_selected_indices(self):
        """
        get list of selected indices
        ---
        """
        return self.chart.selected_points()

    def add_selection_event(self, callback):
        """
        add selection event
        ---
        """
        self.chart.callback = callback

    def apply_theme(self, theme):
        """
        apply thematic changes to the chart based on the input
        properties dictionary.

        """
        if self.no_colors_set:
            self.geo_color_palette = theme.color_palette
            self.compute_colors()
            if self.chart:
                self.chart.colors = self.source[self.rgba_columns]
        if self.map_style is None:
            if self.mapbox_api_key is None:
                self.chart.spec["mapStyle"] = theme.map_style_without_token
            else:
                self.chart.spec["mapStyle"] = theme.map_style
