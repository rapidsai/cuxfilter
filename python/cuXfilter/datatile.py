from .assets.numba_kernels import gpu_datatile
from .charts.core.core_chart import BaseChart
from typing import Type, Tuple

class DataTile:
    dtype: str = 'pandas'
    cumsum: bool = True
    dimensions: int = 2
    active_chart: Type[BaseChart] = None
    passive_chart: Type[BaseChart] = None

    def __init__(self, active_chart: Type[BaseChart], passive_chart: Type[BaseChart], dtype: str ='pandas', dimensions: int =2, cumsum: bool=True):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        self.dtype = dtype
        self.dimensions = dimensions
        self.active_chart = active_chart
        self.passive_chart = passive_chart
        self.cumsum = cumsum
    

    def calc_data_tile(self, data):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        if self.passive_chart.chart_type == 'datasize_indicator':
            return self._calc_data_tile_for_size(data)
        if self.dimensions == 2:
            return self._calc_2d_data_tile(data.copy())

    def _calc_data_tile_for_size(self, data):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        return gpu_datatile.calc_data_tile_for_size(data.copy(), self.active_chart.x, self.active_chart.min_value, self.active_chart.max_value, self.active_chart.stride, cumsum = self.cumsum, return_format= self.dtype)

    # def get_subset_for_groupby_speedup(self,data):
    #     '''
    #     Description: 
    #         groupby compute time increases as the number of columns increase.
    #         Only 2 columns are required for calculating data_tile_for_size, and provides a significant speedup if we take a subset of the dataset
    #     -------------------------------------------
    #     Input:

    #     -------------------------------------------

    #     Ouput:
    #     '''
    #     for i in data.columns.tolist():
    #         if i != self.active_chart.x:
    #             return data[[self.active_chart.x, i]]

    def _calc_2d_data_tile(self, data):
        '''
        Description: 

        -------------------------------------------
        Input:

        -------------------------------------------

        Ouput:
        '''
        return gpu_datatile.calc_data_tile(data, self.active_chart, self.passive_chart, self.passive_chart.aggregate_fn, cumsum=self.cumsum, return_format= self.dtype)



