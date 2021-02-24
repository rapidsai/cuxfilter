import pytest

from cuxfilter.datatile import DataTile
from cuxfilter.charts import bokeh
import cuxfilter
import cudf
import pandas as pd


class TestDataTile:

    bac = bokeh.line("key", "val")
    bac1 = bokeh.bar("val")
    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuxfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(
        charts=[bac, bac1],
        title="test_title",
        layout=cuxfilter.layouts.double_feature,
    )

    def test_variables(self):

        data_tile = DataTile(active_chart=self.bac, passive_chart=self.bac1)

        assert data_tile.dtype == "pandas"
        assert data_tile.cumsum is True
        assert data_tile.active_chart == self.bac
        assert data_tile.passive_chart == self.bac1
        assert data_tile.dimensions == int(2)

    @pytest.mark.parametrize(
        "chart_type, result",
        [("datasize_indicator", "1-d function"), ("bar", "2-d function")],
    )
    def test_calc_data_tile(self, chart_type, result):
        def f1(data):
            return "1-d function"

        def f2(data):
            return "2-d function"

        bac1 = bokeh.bar("val")
        bac1.chart_type = chart_type
        data_tile = DataTile(active_chart=self.bac, passive_chart=bac1)
        data_tile._calc_1d_data_tile = f1
        data_tile._calc_2d_data_tile = f2

        assert data_tile.calc_data_tile(data=cudf.DataFrame()) == result

    def test_calc_1d_data_tile(self):
        datasize_chart = cuxfilter.charts.panel_widgets.data_size_indicator()
        data_tile = DataTile(
            active_chart=self.bac, passive_chart=datasize_chart
        )
        result = pd.DataFrame({0: {0: 1.0, 1: 2.0, 2: 3.0, 3: 4.0, 4: 5.0}})

        assert data_tile._calc_1d_data_tile(self.df).equals(result)

    def test_calc_2d_data_tile(self):
        data_tile = DataTile(active_chart=self.bac, passive_chart=self.bac1)
        result = pd.DataFrame(
            {
                0: {0: 1.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
                1: {0: 1.0, 1: 1.0, 2: 0.0, 3: 0.0, 4: 0.0},
                2: {0: 1.0, 1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0},
                3: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 0.0},
                4: {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
            }
        )
        assert data_tile._calc_2d_data_tile(self.df).equals(result)
