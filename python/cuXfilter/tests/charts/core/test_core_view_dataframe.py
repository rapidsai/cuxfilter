import pytest

import cudf
import panel as pn

from cuXfilter.charts.core.core_view_dataframe import ViewDataFrame
from cuXfilter.charts.core.non_aggregate.core_stacked_line import (
    BaseStackedLine,
)
import cuXfilter


class TestViewDataFrame:
    df = cudf.DataFrame(
        {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
    )
    cux_df = cuXfilter.DataFrame.from_dataframe(df)
    dashboard = cux_df.dashboard(charts=[], title="test_title")

    def test_variables(self):
        vd = ViewDataFrame()

        vd.chart_type == "view_dataframe"
        vd.columns is None
        vd._width == 400
        vd._height == 400
        vd.use_data_tiles is False
        vd.source is None
        vd.chart is None
        vd.name == "view_dataframe"

    def test_initiate_chart(self):
        vd = ViewDataFrame()
        assert vd.columns is None

        vd.initiate_chart(self.dashboard)

        assert str(vd.chart.objects[0]) == str(
            pn.pane.HTML(
                self.df,
                style={
                    "width": "100%",
                    "height": "100%",
                    "overflow-y": "auto",
                    "font-size": "0.5vw",
                    "overflow-x": "auto",
                },
            )
        )
        assert vd.chart.sizing_mode == "scale_both"
        assert vd.columns == list(self.df.columns)

    @pytest.mark.parametrize("chart, _chart", [(None, None), (1, 1)])
    def test_view(self, chart, _chart):
        vd = ViewDataFrame()
        vd.chart = chart

        assert vd.view() == _chart

    def test_reload_chart(self):
        vd = ViewDataFrame()
        vd.initiate_chart(self.dashboard)
        vd.reload_chart(self.df, patch_update=False)

        assert vd.chart[0].object.equals(self.df)

    @pytest.mark.parametrize(
        "width, height, result1, result2",
        [(400, 400, 400, 400), (None, None, 400, 400)],
    )
    def test_update_dimensions(self, width, height, result1, result2):
        vd = ViewDataFrame()
        vd.initiate_chart(self.dashboard)
        vd.width, vd.height = 400, 400
        vd.update_dimensions(width=width, height=height)

        assert vd.chart.width == result1
        assert vd.chart.height == result2

    def test_query_chart_by_range(self):
        bsl = ViewDataFrame()
        bsl_1 = BaseStackedLine("b", ["a"])
        query_tuple = (4, 5)
        df = cudf.DataFrame([("a", [1, 2, 3, 4]), ("b", [3, 4, 5, 6])])
        bsl.source = df
        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bsl.reload_chart = t_func
        bsl.query_chart_by_range(
            active_chart=bsl_1, query_tuple=query_tuple, data=df
        )

        assert self.result.to_string() == "   a  b\n1  2  4\n2  3  5"
        assert self.patch_update is False

    @pytest.mark.parametrize(
        "new_indices, result",
        [
            ([4, 5], "   a  b\n1  2  4\n2  3  5"),
            ([], "   a  b\n0  1  3\n1  2  4\n2  3  5\n3  4  6"),
            ([3], "   a  b\n0  1  3"),
        ],
    )
    def test_query_chart_by_indices(self, new_indices, result):
        bsl = ViewDataFrame()
        bsl_1 = BaseStackedLine("b", ["a"])
        new_indices = new_indices
        df = cudf.DataFrame([("a", [1, 2, 3, 4]), ("b", [3, 4, 5, 6])])
        bsl.source = df
        self.result = None
        self.patch_update = None

        def t_func(data, patch_update):
            self.result = data
            self.patch_update = patch_update

        # creating a dummy reload chart fn as its not implemented in core
        # non aggregate chart class
        bsl.reload_chart = t_func
        bsl.query_chart_by_indices(
            active_chart=bsl_1,
            old_indices=[],
            new_indices=new_indices,
            data=df,
        )

        assert self.result.to_string() == result
        assert self.patch_update is False
