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

    def calc_data_tile(self, data):
        """
        calc data tiles base function
        """
        if self.passive_chart.chart_type == "datasize_indicator":
            return self._calc_data_tile_for_size(data)
        if self.dimensions == 2:
            return self._calc_2d_data_tile(data.copy())

    def _calc_data_tile_for_size(self, data):
        """
        calc data tiles for dataset size
        """
        return gpu_datatile.calc_data_tile_for_size(
            data.copy(),
            self.active_chart.x,
            self.active_chart.min_value,
            self.active_chart.max_value,
            self.active_chart.stride,
            cumsum=self.cumsum,
            return_format=self.dtype,
        )

    def _calc_2d_data_tile(self, data):
        """
        calc data tiles
        """
        return gpu_datatile.calc_data_tile(
            data,
            self.active_chart,
            self.passive_chart,
            self.passive_chart.aggregate_fn,
            cumsum=self.cumsum,
            return_format=self.dtype,
        )
