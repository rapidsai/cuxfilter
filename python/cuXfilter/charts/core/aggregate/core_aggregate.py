import numpy as np
from typing import Dict
from ..core_chart import BaseChart

class BaseAggregateChart(BaseChart):

    use_data_tiles = True

    def query_chart_by_range(self, active_chart, query_tuple, datatile):
        '''
        Description: 

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: datatile of active chart for current chart[type:pandas df]
        -------------------------------------------

        Ouput:
        '''
        min_val, max_val = query_tuple
        datatile_index_min = int(round((min_val - active_chart.min_value)/active_chart.stride))
        datatile_index_max = int(round((max_val - active_chart.min_value)/active_chart.stride))
        
        if datatile_index_min == 0:
            
            if self.aggregate_fn == 'mean':
                datatile_result_sum = np.array(datatile[0].loc[:, datatile_index_max])
                datatile_result_count = np.array(datatile[1].loc[:, datatile_index_max])
                datatile_result = datatile_result_sum/datatile_result_count
            elif self.aggregate_fn == 'count':
                datatile_result = datatile.loc[:, datatile_index_max]
        
        else:
            datatile_index_min -= 1
            if self.aggregate_fn == 'mean':
                datatile_result_sum = np.array(datatile[0].loc[:, datatile_index_max] - datatile[0].loc[:, datatile_index_min])
                datatile_result_count = np.array(datatile[1].loc[:, datatile_index_max] - datatile[1].loc[:, datatile_index_min])
                datatile_result = datatile_result_sum/datatile_result_count
            elif self.aggregate_fn == 'count':
                datatile_result = datatile.loc[:, datatile_index_max] - datatile.loc[:, datatile_index_min]

        self.reset_chart(datatile_result)


    def query_chart_by_indices_for_mean(self, active_chart, old_indices, new_indices, datatile, calc_new, remove_old):
        '''
        Description: 

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        '''
        if len(new_indices) == 0 or new_indices == ['']:
            datatile_result = np.array( datatile[0].sum(axis=1, skipna=True)) / np.array( datatile[1].sum(axis=1, skipna=True))
            return datatile_result

        datatile_result = np.zeros(shape=(len(self.get_source_y_axis()),), dtype=np.float64)
        value_sum = np.zeros(shape=(len(self.get_source_y_axis()),), dtype=np.float64)
        value_count = np.zeros(shape=(len(self.get_source_y_axis()),), dtype=np.float64)
        
        for index in new_indices:
            index = int(round((index - active_chart.min_value)/active_chart.stride))
            value_sum += datatile[0][int(index)][:self.data_points]
            value_count += datatile[1][int(index)][:self.data_points]

        datatile_result = value_sum/value_count
            
        return datatile_result


    def query_chart_by_indices_for_count(self, active_chart, old_indices, new_indices, datatile, calc_new, remove_old):
        '''
        Description: 

        -------------------------------------------
        Input:
        -------------------------------------------

        Ouput:
        '''
        if len(new_indices) == 0 or new_indices == ['']:
            datatile_result = np.array( datatile.sum(axis=1, skipna=True))
            return datatile_result

        if len(old_indices) == 0 or old_indices == ['']:
            datatile_result = np.zeros(shape=(len(self.get_source_y_axis()),), dtype=np.float64)
        else:    
            datatile_result = np.array(self.get_source_y_axis(), dtype=np.float64)

        for index in calc_new:
            index = int(round((index - active_chart.min_value)/active_chart.stride))
            datatile_result += np.array( datatile[int(index)][:self.data_points] )
            
        for index in remove_old:
            index = int(round((index - active_chart.min_value)/active_chart.stride))
            datatile_result -= np.array( datatile[int(index)][:self.data_points] )
           
        return datatile_result

    def query_chart_by_indices(self, active_chart, old_indices, new_indices, datatile):
        '''
        Description: 

        -------------------------------------------
        Input:
            1. active_chart: chart object of active_chart
            2. query_tuple: (min_val, max_val) of the query [type: tuple]
            3. datatile: datatile of active chart for current chart[type:pandas df]
        -------------------------------------------

        Ouput:
        '''
        calc_new = list(set(new_indices) - set(old_indices))
        remove_old = list(set(old_indices) - set(new_indices))

        if '' in calc_new: calc_new.remove('') 
        if '' in remove_old: remove_old.remove('') 


        if self.aggregate_fn == 'mean':
            datatile_result = self.query_chart_by_indices_for_mean(active_chart, old_indices, new_indices, datatile, calc_new, remove_old)
        else:
            datatile_result = self.query_chart_by_indices_for_count(active_chart, old_indices, new_indices, datatile, calc_new, remove_old)
 
        self.reset_chart(datatile_result)