import pytest
from cuxfilter import charts
from cuxfilter import DataFrame
from cuxfilter.charts.deckgl.bindings import PanelDeck

from ..utils import initialize_df, df_types

df_args = {
    "states": [float(i + 30) for i in range(10)],
    "val": [float(i + 10) for i in range(10)],
    "val_t": [float(i + 100) for i in range(10)],
}
dfs = [initialize_df(type, df_args) for type in df_types]
cux_dfs = [DataFrame.from_dataframe(df) for df in dfs]


class TestDeckGL:
    @pytest.mark.parametrize("cux_df", cux_dfs)
    def test_init(self, cux_df):
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
            "mapStyle": None,
            "initialViewState": {
                "latitude": 28.400005999999998,
                "longitude": 0.31556500000000653,
                "zoom": 3,
                "max_zoom": 16,
            },
            "controller": True,
            "layers": [
                {
                    "@@type": "PolygonLayer",
                    "opacity": 1,
                    "getLineWidth": 10,
                    "getPolygon": "@@=coordinates",
                    "getElevation": "@@=val_t*100000",
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
                    "id": "PolygonLayer-states_count_choropleth_states",
                    "data": choropleth3d_chart.source,
                }
            ],
        }

        assert isinstance(choropleth3d_chart.chart, PanelDeck)

        assert choropleth3d_chart.chart.x == "states"
        assert choropleth3d_chart.chart.data.equals(choropleth3d_chart.source)

        assert choropleth3d_chart.chart.colors.equals(
            choropleth3d_chart.source[choropleth3d_chart.rgba_columns],
        )

        assert choropleth3d_chart.chart.indices == set()

        assert choropleth3d_chart.chart.multi_select is False

        assert choropleth3d_chart.chart.sizing_mode == "stretch_both"
