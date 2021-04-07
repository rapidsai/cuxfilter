import pytest

from cuxfilter import DataFrame
import cuxfilter
import cudf


class TestDataFrame:
    @pytest.mark.parametrize(
        "cux_df", [(DataFrame.from_dataframe(cudf.DataFrame()))]
    )
    def test_init(self, cux_df):
        assert isinstance(cux_df.data, cudf.DataFrame)
        assert cux_df.data.equals(cudf.DataFrame())
        assert cux_df.is_graph is False
        assert cux_df.edges is None

    def test_dashboard(self):
        df = cudf.DataFrame(
            {"key": [0, 1, 2, 3, 4], "val": [float(i + 10) for i in range(5)]}
        )
        cux_df = DataFrame.from_dataframe(df)

        dashboard = cux_df.dashboard(charts=[], title="test_title")

        assert dashboard._cuxfilter_df.data.equals(df)
        assert dashboard.title == "test_title"
        assert (
            dashboard._dashboard.__class__ == cuxfilter.layouts.single_feature
        )
        assert dashboard._theme == cuxfilter.themes.light
