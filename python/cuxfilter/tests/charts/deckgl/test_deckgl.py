import pytest
import cudf

from cuxfilter import charts
from cuxfilter import DataFrame
from cuxfilter.charts.deckgl.bindings import panel_deck

pytest


class TestDeckGL:
    def test_init(self):
        cux_df = DataFrame.from_dataframe(
            cudf.DataFrame(
                {
                    "states": [float(i + 30) for i in range(10)],
                    "val": [float(i + 10) for i in range(10)],
                    "val_t": [float(i + 100) for i in range(10)],
                }
            )
        )

        choropleth3d_chart = charts.choropleth(
            x="states",
            color_column="val",
            elevation_column="val_t",
            color_aggregate_fn="mean",
            elevation_aggregation_fn="count",
            data_points=57,
            add_interaction=False,
            elevation_factor=100000,
            geoJSONSource=(
                "https://raw.githubusercontent.com/loganpowell/census-geojson"
                "/master/GeoJSON/5m/2018/state.json"
            ),
            geoJSONProperty="STATEFP",
        )

        cux_df.dashboard([choropleth3d_chart])

        assert isinstance(choropleth3d_chart, charts.deckgl.plots.Choropleth)

        assert choropleth3d_chart.deck_spec == {
            "mapboxApiAccessToken": None,
            "mapStyle": "mapbox://styles/mapbox/dark-v9",
            "initialViewState": {
                "latitude": 28.400005999999998,
                "longitude": 0.31556500000000653,
                "zoom": 3,
                "max_zoom": 16,
            },
            "controller": True,
            "layers": [
                {
                    "opacity": 1,
                    "getLineWidth": 10,
                    "getPolygon": "coordinates",
                    "getElevation": "val_t*100000",
                    "getFillColor": "[__r__, __g__, __b__, __a__]",
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
            ],
        }

        assert isinstance(choropleth3d_chart.chart, panel_deck)

        assert choropleth3d_chart.chart.x == "states"
        assert choropleth3d_chart.chart.data.equals(
            choropleth3d_chart.source_df
        )

        assert choropleth3d_chart.chart.colors.equals(
            choropleth3d_chart.source_df[choropleth3d_chart.rgba_columns],
        )

        assert choropleth3d_chart.chart.indices == set()

        assert choropleth3d_chart.chart.multi_select is False

        assert choropleth3d_chart.chart.sizing_mode == "scale_both"
