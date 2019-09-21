#cuXfilter_utils.py

from pyarrow import RecordBatchStreamReader
from app.utilities.numbaHistinMem import numba_gpu_histogram
from cudf.dataframe import DataFrame
import cudf
import json
import os
import numpy as np
import time
import sys
import gc
import pickle
from numba import cuda
from app import app

def default(o):
    if isinstance(o, np.int8) or isinstance(o, np.int16) or isinstance(o, np.int32) or isinstance(o, np.int64): return int(o)
    elif isinstance(o, np.float16) or isinstance(o, np.float32) or isinstance(o, np.float64): return float(o)
    raise TypeError

class cuXfilter_utils:
    data_gpu = None
    back_up_dimension = None
    dimensions_filters = {}
    group_by_backups = {}


    def __init__(self):
        self.data_gpu = None
        self.back_up_dimension = None
        self.dimensions_filters = {}
        self.dimensions_filters_response_format = {}
        self.group_by_backups = {}

    def hist_numba_GPU(self,data,bins):
        '''
            description:
                Calculate histogram leveraging gpu via pycuda(using numba jit)
            input:
                data: cudf row as a series -> gpu mem pointer, bins: number of bins in the histogram
            Output:
                json -> {X:[__values_of_colName_with_max_64_bins__], Y:[__frequencies_per_bin__]}
        '''
        try:
            df1 = numba_gpu_histogram(data,int(bins))
            del data
            dict_temp ={}

            dict_temp['X'] = list(df1[1].astype(float))
            dict_temp['Y'] = list(df1[0].astype(float))

            return str(json.dumps(dict_temp))
        except Exception as e:
            return 'Exception *** in cudf hist_numba_GPU():'+str(e)

    def groupby(self,data,column_name, groupby_agg,groupby_agg_key):
        '''
            description:
                Calculate groupby on a given column on the cudf
            input:
                data: cudf row as a series -> gpu mem pointer,
                column_name: column name
            Output:
                json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
        '''
        try:
            group_appl = data.groupby(by=[column_name], as_index=False).agg(groupby_agg)
            key = column_name+"_"+groupby_agg_key
            self.group_by_backups[key] = True
        except Exception as e:
            return "Exception *** in cudf groupby(): "+str(e)

        return group_appl

    def get_columns(self):
        '''
            description:
            Column names in a data frame
            input:
                data: pandas df
            Output:
                list of column names
        '''
        try:
            return str(list(self.data_gpu.columns))
        except Exception as e:
            return "Exception *** in cudf get_columns():"+str(e)

    def readArrow(self,source):
        '''
            description:
                Read arrow file from disk using apache pyarrow
            input:
                source: file path
            return:
                pyarrow table
        '''
        reader = RecordBatchStreamReader(source)
        pa_df = reader.read_all()
        return pa_df

    def read_arrow_to_DF(self,source):
        '''
            description:
                Read arrow file from disk using apache pyarrow
            input:
                source: file path
            return:
                status
        '''
        source = source+".arrow"
        try:
            self.data_gpu = cudf.DataFrame.from_arrow(self.readArrow(source))
            # for i in pa_df.columns:
            #     self.data_gpu[i] = cudf.Series(np.array(pa_df[i].values))
            if 'nonfilter' not in source:
                self.back_up_dimension = self.data_gpu
            # del(pa_df)
            gc.collect()
        except Exception as e:
            # del(pa_df)
            del(self.data_gpu)
            del(self.back_up_dimension)
            gc.collect()
            return "Exception *** in cudf read_arrow_to_DF():"+str(e)

        return "data read successfully"

    def read_ipc_to_DF(self,source):
        '''
            description:
                Read arrow file from another dataframe already in the gpu
            input:
                source: file path
            return:
                pandas dataframe
        '''

        try:
            with open(source+'.pickle', 'rb') as handle:
                buffer = eval(pickle.load(handle))
            with open(source+'-col.pickle', 'rb') as handle:
                columns = list(pickle.load(handle))
            self.data_gpu = DataFrame()

            for i,j in enumerate(buffer):
                temp_ipc_handler = pickle.loads(j)
                with temp_ipc_handler as temp_nd_array:
                    np_arr = np.zeros((temp_nd_array.size), dtype=temp_nd_array.dtype)
                    np_arr_gpu = cuda.to_device(np_arr)
                    np_arr_gpu.copy_to_device(temp_nd_array)
                    self.data_gpu[columns[i]] = cudf.Series(np_arr_gpu)

            self.back_up_dimension = self.data_gpu

        except Exception as e:
            del(self.data_gpu)
            del(self.back_up_dimension)
            gc.collect()
            return "Exception *** in cudf read_ipc_to_DF():"+str(e)

        return "data read successfully"



    def read_data(self,load_type,file):
        '''
            description:
                Read file as per the load type
            input:
                load_type: csv or arrow or ipc
                file: file path
            return:
                pandas dataframe
        '''
        #file is in the uploads/ folder, so append that to the path
        file = str("/usr/src/app/node_server/uploads/"+file)
        if load_type == 'arrow':
            status = self.read_arrow_to_DF(file)
        elif load_type == 'ipc':
            status = self.read_ipc_to_DF(file)
        return status


    def parse_dict(self,data):
        '''
            description:
                get parsed string format of the dictionary, that can be sent to the socket-client
            input:
                data: dataframe
            return:
                shape string
        '''
        try:
            temp_dict = {}
            for i in data:
                temp_dict[i] = list(data[i].values())
            return json.dumps(temp_dict,default=default)
        except Exception as e:
            return 'Exception *** in cudf parse_dict() (helper function):'+str(e)

    def get_size(self):
        '''
            description:
                get shape of the dataframe
            input:
                data: dataframe
            return:
                shape tuple
        '''
        try:
            return str(len(self.data_gpu))
        except Exception as e:
            return 'Exception *** in cudf get_size():'+str(e)

    def reset_filters(self, data, omit=None, include_dim=['all']):
        '''
            description:
                reset filters on the data_gpu dataframe by executing all filters in the dimensions_filters dictionary
            input:
                data: dataset
                omit: column name, the filters associated to which, are to be omitted
                include_dim: list of column_names, which are to be included along with dimensions_filters.keys(); ['all'] to include all columns

            Output:
                result dataframe after executing the filters using the dataframe.query() command
        '''
        try:
            start_time = time.perf_counter()
            temp_list = []
            for key in self.dimensions_filters.keys():
                if omit is not None and omit == key:
                    continue
                if len(self.dimensions_filters[key])>0:
                    temp_list.append(self.dimensions_filters[key])
            query = ' and '.join(temp_list)
            if(len(query) > 0):
                if include_dim[0] == 'all':
                    return data.query(query)
                else:
                    column_list = list(set(list(self.dimensions_filters.keys())+include_dim))
                    try:
                        #app.logger.debug(query)
                        #app.logger.debug('executing the query command now')
                        return data.loc[:,column_list].query(query)
                    except Exception as e:
                        return 'Exception *** in cudf reset_filters():'+str(e)
                    # return return_val
            else:
                return data

        except Exception as e:
            return 'Exception *** '+str(e)


    def numba_jit_warm_func(self):
        '''
            description:
                send dummy call to numba_gpu_histogram to precompile jit function
            input:
                None
            Output:
                None
        '''
        try:
            self.hist_numba_GPU(self.data_gpu[self.data_gpu.columns[-1]].to_gpu_array(),640)
        except Exception as e:
            return 'Exception *** in cudf numba_jit_warm_func():'+str(e)


    def reset_all_filters(self):
        '''
            description:
                reset all filters on all dimensions for the dataset
            input:
                None
            Output:
                number_of_rows_left
        '''
        try:
            self.data_gpu = self.back_up_dimension
            for key in self.dimensions_filters.keys():
                self.dimensions_filters[key] = ''
                self.dimensions_filters_response_format[key]=[]
            return str(len(self.data_gpu))

        except Exception as e:
            return 'Exception *** in cudf reset_all_filters:'+str(e)

    def groupby_load(self, dimension_name, groupby_agg, groupby_agg_key):
        '''
            description:
                load groupby operation for dimension as per the given groupby_agg
            input:
                dimension_name <string>:
                groupby_agg <dictionary>:
                groupby_agg_key <string>:
            return:
                status: groupby intialized successfully
        '''
        try:
            key = dimension_name+"_"+groupby_agg_key
            self.group_by_backups[key] = True
            response = 'groupby initialized successfully'
            return response+"&0"
        except Exception as e:
            return 'Exception *** in cudf groupby_load():'+str(e)

    def groupby_filter_order(self, dimension_name, groupby_agg, groupby_agg_key, sort_order, num_rows, sort_column):
        '''
            description:
                get groupby values by a filter_order(all, top(n), bottom(n)) for a groupby on a dimension
            Get parameters:
                dimension_name (string)
                groupby_agg (JSON stringified object)
                groupby_agg_key <string>:
                sort_order (string): top/bottom/all
                num_rows (integer): OPTIONAL -> if sort_order= top/bottom
                sort_column: column name by which the result should be sorted
            Response:
                all rows/error => "groupby not initialized"
        '''
        try:
            key = dimension_name+"_"+groupby_agg_key
            if(key not in self.group_by_backups):
                res = "groupby not intialized"
            else:
                #removing the cumulative filters on the current dimension for the groupby
                #app.logger.debug(dimension_name)
                #app.logger.debug(list(groupby_agg.keys()))
                temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name,include_dim=list(groupby_agg.keys()))
                groupby_result = self.groupby(temp_df,dimension_name,groupby_agg,groupby_agg_key)
                if 'all' == sort_order:
                    temp_df = groupby_result.to_pandas().to_dict() #self.group_by_backups[key].to_pandas().to_dict()
                else:
                    max_rows = max(len(groupby_result)-1,0) #max(len(self.group_by_backups[key])-1,0)
                    n_rows = min(num_rows,max_rows)
                    try:
                        if 'top' == sort_order:
                            temp_df = groupby_result.nlargest(n_rows,[sort_column]).to_pandas().to_dict()
                        elif 'bottom' == sort_order:
                            temp_df = groupby_result.nsmallest(n_rows,[sort_column]).to_pandas().to_dict()
                    except Exception as e:
                        return 'Exception *** in cudf groupby_filter_order():'+str(e)
                res = str(self.parse_dict(temp_df))
            return res

        except Exception as e:
            return 'Exception *** '+str(e)

    def dimension_load(self, dimension_name):
        '''
            description:
                load a dimension
            Get parameters:
                dimension_name (string)
            Response:
                status -> success: dimension loaded successfully/dimension already exists   // error: "groupby not initialized"
        '''
        try:
            if dimension_name not in self.dimensions_filters:
                self.dimensions_filters[dimension_name] = ''
                self.dimensions_filters_response_format[dimension_name] = []
                res = 'dimension loaded successfully'
            else:
                res = 'dimension already exists'
            return res

        except Exception as e:
            return 'Exception *** in cudf dimension_load():'+str(e)

    def dimension_reset(self, dimension_name):
        '''
            description:
                reset all filters on a dimension
            Get parameters:
                dimension_name (string)
            Response:
                number_of_rows
        '''
        try:
            self.data_gpu = self.back_up_dimension
            self.dimensions_filters[dimension_name] = ''
            self.dimensions_filters_response_format[dimension_name] = []
            self.data_gpu = self.reset_filters(self.data_gpu)
            return str(len(self.data_gpu))

        except Exception as e:
            return 'Exception *** in cudf dimension_reset():'+str(e)


    def dimension_get_max_min(self, dimension_name):
        '''
            description:
                get_max_min for a dimension
            Get parameters:
                dimension_name (string)
            Response:
                max_min_tuple
        '''
        try:
            max_min_tuple = (float(self.data_gpu[dimension_name].min()), float(self.data_gpu[dimension_name].max()))
            return str(max_min_tuple)

        except Exception as e:
            return 'Exception *** in cudf dimension_get_max_min():'+str(e)

    def dimension_hist(self, dimension_name, num_of_bins):
        '''
            description:
                get histogram for a dimension
            Get parameters:
                dimension_name (string)
                num_of_bins (integer)
            Response:
                string(json) -> "{X:[__values_of_colName_with_max_64_bins__], Y:[__frequencies_per_bin__]}"
        '''
        try:
            num_of_bins = int(num_of_bins)
            if len(self.dimensions_filters.keys()) == 0 or (dimension_name not in self.dimensions_filters) or (dimension_name in self.dimensions_filters and self.dimensions_filters[dimension_name] == ''):
                return str(self.hist_numba_GPU(self.data_gpu[str(dimension_name)].to_gpu_array(),num_of_bins))
            else:
                temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name, include_dim = [dimension_name])
                return_val = str(self.hist_numba_GPU(temp_df[str(dimension_name)].to_gpu_array(),num_of_bins))
                del temp_df
                return return_val

        except Exception as e:
            return 'Exception *** in cudf dimension_hist():'+str(e)


    def dimension_filter_order(self, dimension_name, sort_order, num_rows, columns):
        '''
            description:
                get columns values by a filter_order(all, top(n), bottom(n)) sorted by dimension_name
            Get parameters:
                dimension_name (string)
                sort_order (string): top/bottom/all
                num_rows (integer): OPTIONAL -> if sort_order= top/bottom
                columns (string): comma separated column names
            Response:
                string(json) -> "{col_1:[__row_values__], col_2:[__row_values__],...}"
        '''
        try:
            columns = columns.split(',')
            if(len(columns) == 0 or columns[0]==''):
                columns = list(self.data_gpu.columns)
            elif dimension_name not in columns:
                columns.append(dimension_name)

            if 'all' == sort_order:
                temp_df = self.data_gpu.loc[:,list(columns)].to_pandas().to_dict()
            else:
                num_rows = int(num_rows)
                max_rows = max(len(self.data_gpu)-1,0)
                n_rows = min(num_rows, max_rows)
                try:
                    if 'top' == sort_order:
                        temp_df = self.data_gpu.loc[:,list(columns)].nlargest(n_rows,[dimension_name]).to_pandas().to_dict()
                    elif 'bottom' == sort_order:
                        temp_df = self.data_gpu.loc[:,list(columns)].nsmallest(n_rows,[dimension_name]).to_pandas().to_dict()
                except Exception as e:
                    return 'Exception *** in cudf dimension_filter_order(1):'+str(e)

            return str(self.parse_dict(temp_df))

        except Exception as e:
            return 'Exception *** in cudf dimension_filter_order(2):'+str(e)

    def dimension_filter(self, dimension_name, comparison_operation, value, pre_reset):
        '''
            description:
                cumulative filter dimension_name by comparison_operation and value
            Get parameters:
                dimension_name (string)
                comparison_operation (string)
                value (float/int)
            Response:
                number_of_rows_left
        '''
        try:
            temp_list = []
            #implementation of resetThenFilter function
            if pre_reset == True:
                self.dimension_reset(dimension_name)

            if type(eval(value)) == type(tuple()):
                val_list = list(eval(value))
                query_list = []
                for v in val_list:
                    query_list.append(str(dimension_name+comparison_operation+str(v)))
                query = ' or '.join(query_list)
                query = '('+query+')'
            else:
                query = dimension_name+comparison_operation+value

            if dimension_name in self.dimensions_filters:
                if len(self.dimensions_filters[dimension_name])>0:
                    self.dimensions_filters[dimension_name] += ' and '+ query
                else:
                    self.dimensions_filters[dimension_name] = query
                self.dimensions_filters_response_format[dimension_name] = [value,value]

            try:
                self.data_gpu = self.data_gpu.query(query)
            except Exception as e:
                return 'Exception *** in cudf dimension_filter(1):'+str(e)
            return str(len(self.data_gpu))

        except Exception as e:
            return 'Exception *** in cudf dimension_filter(2):'+str(e)

    def dimension_filter_range(self, dimension_name, min_value, max_value, pre_reset):
        '''
            description:
                cumulative filter_range dimension_name between range [min_value,max_value]
            Get parameters:
                dimension_name (string)
                min_value (integer)
                max_value (integer)
            Response:
                number_of_rows_left
        '''
        try:
            if pre_reset == True:
                #implementation of resetThenFilter function
                self.dimension_reset(dimension_name)

            query = dimension_name+">="+min_value+" and "+dimension_name+"<="+max_value
            if dimension_name in self.dimensions_filters:
                if len(self.dimensions_filters[dimension_name])>0:
                    self.dimensions_filters[dimension_name] += ' and '+ query
                else:
                    self.dimensions_filters[dimension_name] = query
                self.dimensions_filters_response_format[dimension_name] = [min_value,max_value]
            try:
                self.data_gpu = self.data_gpu.query(query)
            except Exception as e:
                return 'Exception *** in cudf dimension_filter_range(1):'+str(e)
            return str(len(self.data_gpu))
        except Exception as e:
            return 'Exception *** in cudf dimension_filter_range(2):'+str(e)
