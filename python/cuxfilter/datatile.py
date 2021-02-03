from typing import Type

from .assets.numba_kernels import gpu_datatile
from .charts.core.core_chart import BaseChart


class DataTile:
    dtype: str = "pandas"
    cumsum: bool = True
    dimensions: int = 2
    active_chart: Type[BaseChart] = None
    passive_chart: Type[BaseChart] = None

    def __init__(
        self,
        active_chart: Type[BaseChart],
        passive_chart: Type[BaseChart],
        dtype: str = "pandas",
        dimensions: int = 2,
        cumsum: bool = True,
    ):
        """
        init function
        """
        self.dtype = dtype
        self.dimensions = dimensions
        self.active_chart = active_chart
        self.passive_chart = passive_chart
        self.cumsum = cumsum

    def calc_data_tile(self, data, query=""):
        """
        calc data tiles base function
        """
        if len(query) > 0:
            data = data.query(str(query))
        if self.passive_chart.chart_type in [
            "number_chart",
            "number_chart_widget",
            "datasize_indicator",
        ]:
            return self._calc_1d_data_tile(data)
        elif self.passive_chart.chart_type == "choropleth":
            return self._calc_choropleth_data_tile(data)
        if self.dimensions == 2:
            return self._calc_2d_data_tile(data)

    def _calc_1d_data_tile(self, data):
        """
        calc data tiles for dataset size
        """
        return gpu_datatile.calc_1d_data_tile(
            data,
            self.active_chart,
            self.passive_chart,
            cumsum=self.cumsum,
            return_format=self.dtype,
        )

    def _calc_2d_data_tile(self, data):
        """
        calc data tiles
        """
        # cumsum has to be false for aggregate charts with agg_fn = min/max
        if self.cumsum and self.passive_chart.aggregate_fn in ["min", "max"]:
            self.cumsum = False
        return_result = gpu_datatile.calc_data_tile(
            data,
            self.active_chart,
            self.passive_chart,
            self.passive_chart.aggregate_fn,
            cumsum=self.cumsum,
            return_format=self.dtype,
        )
        return return_result

    def _calc_choropleth_data_tile(self, data):
        """
        calc multiple data tiles for color and elevation agg for 3d choropleth
        """
        ret_datatile = {}
        self.passive_chart.y = self.passive_chart.color_column
        cumsum = self.cumsum
        # cumsum has to be false for aggregate charts with agg_fn = min/max
        if self.cumsum and self.passive_chart.color_aggregate_fn in [
            "min",
            "max",
        ]:
            cumsum = False

        ret_datatile[
            self.passive_chart.color_column
        ] = gpu_datatile.calc_data_tile(
            data,
            self.active_chart,
            self.passive_chart,
            self.passive_chart.color_aggregate_fn,
            cumsum=cumsum,
            return_format=self.dtype,
        )
        if self.passive_chart.elevation_column is not None:
            cumsum = self.cumsum
            # cumsum has to be false for aggregate charts with agg_fn = min/max
            if self.cumsum and self.passive_chart.elevation_aggregate_fn in [
                "min",
                "max",
            ]:
                cumsum = False
            self.passive_chart.y = self.passive_chart.elevation_column
            ret_datatile[
                self.passive_chart.elevation_column
            ] = gpu_datatile.calc_data_tile(
                data,
                self.active_chart,
                self.passive_chart,
                self.passive_chart.elevation_aggregate_fn,
                cumsum=cumsum,
                return_format=self.dtype,
            )
        return ret_datatile
