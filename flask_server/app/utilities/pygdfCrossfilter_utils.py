from pyarrow import RecordBatchStreamReader
from app.utilities.numbaHistinMem import numba_gpu_histogram
from pygdf.dataframe import DataFrame
import pygdf
import json
import os
import numpy as np
import time
import sys
import gc
import pickle
from numba import cuda

def default(o):
    if isinstance(o, np.int32): return int(o)
    if isinstance(o, np.int64): return int(o)
    if isinstance(o, np.float32): return float(o)
    if isinstance(o, np.float64): return float(o)
    raise TypeError

class pygdfCrossfilter_utils:
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
                data: pygdf row as a series -> gpu mem pointer, bins: number of bins in the histogram
            Output:
                json -> {X:[__values_of_colName_with_max_64_bins__], Y:[__frequencies_per_bin__]}
        '''
        print("calculating histogram")
        df1 = numba_gpu_histogram(data,int(bins))
        dict_temp ={}

        dict_temp['X'] = list(df1[1].astype(float))
        dict_temp['Y'] = list(df1[0].astype(float))

        return str(json.dumps(dict_temp))

    def groupby(self,data,column_name, groupby_agg,groupby_agg_key):
        '''
            description:
                Calculate groupby on a given column on the pygdf
            input:
                data: pygdf row as a series -> gpu mem pointer,
                column_name: column name
            Output:
                json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
        '''
        # global group_by_backups
        print(column_name)
        print("inside groupby function")
        try:
            group_appl = data.groupby(by=[column_name]).agg(groupby_agg)
        except Exception as e:
            del(self.data_gpu)
            del(self.back_up_dimension)
            return "oom error, please reload"
        print(len(group_appl))
        key = column_name+"_"+groupby_agg_key
        self.group_by_backups[key] = group_appl  #.loc[:,[column_name,column_name+'_'+agg]]
        return "groupby intialized successfully"

    def get_columns(self):
        '''
            description:
            Column names in a data frame
            input:
                data: pandas df
            Output:
                list of column names
        '''
        return str(list(self.data_gpu.columns))

    def read_arrow_to_DF(self,source):
        '''
            description:
                Read arrow file from disk using apache pyarrow
            input:
                source: file path
            return:
                pandas dataframe
        '''
        source = source+".arrow"
        pa_df = RecordBatchStreamReader(source).read_all().to_pandas()
        try:
            self.data_gpu = DataFrame()
            for i in pa_df.columns:
                self.data_gpu[i] = pygdf.Series(np.array(pa_df[i].values))
            if 'nonfilter' not in source:
                self.back_up_dimension = self.data_gpu
            del(pa_df)
            gc.collect()
        except Exception as e:
            del(pa_df)
            del(self.data_gpu)
            del(self.back_up_dimension)
            gc.collect()
            return "oom error, please reload"+str(e)

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
        with open(source+'.pickle', 'rb') as handle:
            buffer = eval(pickle.load(handle))
        with open(source+'-col.pickle', 'rb') as handle:
            columns = list(pickle.load(handle))
        try:
            self.data_gpu = DataFrame()
            for i,j in enumerate(buffer):
                temp_ipc_handler = pickle.loads(j)
                with temp_ipc_handler as temp_nd_array:
                    np_arr = np.zeros((temp_nd_array.size), dtype=temp_nd_array.dtype)
                    np_arr_gpu = cuda.to_device(np_arr)
                    np_arr_gpu.copy_to_device(temp_nd_array)
                    self.data_gpu[columns[i]] = pygdf.Series(np_arr_gpu)

            self.back_up_dimension = self.data_gpu
        except Exception as e:
            del(self.data_gpu)
            del(self.back_up_dimension)
            gc.collect()
            return "oom error, please reload"+str(e)

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
            return str(e)

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
            return str((len(self.data_gpu),len(self.data_gpu.columns)))
        except Exception as e:
            return str(e)

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
        # global dimensions_filters
        # print("inside reset filters")
        try:
            temp_list = []
            for key in self.dimensions_filters.keys():
                if omit is not None and omit == key:
                    continue
                if len(self.dimensions_filters[key])>0:
                    temp_list.append(self.dimensions_filters[key])
            query = ' and '.join(temp_list)
            if(len(query) >0):
                # return data.query(query)
                if include_dim[0] == 'all':
                    return data.query(query)
                else:
                    column_list = list(set(list(self.dimensions_filters.keys())+include_dim))
                    try:
                        return_val = data.loc[:,column_list].query(query)
                    except Exception as e:
                        del(self.data_gpu)
                        del(self.back_up_dimension)
                        print("******** oom error **********")
                        return 'oom error, please reload'
                    return return_val
            else:
                return data

        except Exception as e:
            return str(e)


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
            return str(e)


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
            self.dimensions_filters.clear()
            self.dimensions_filters_response_format.clear()
            return str(len(self.data_gpu))

        except Exception as e:
            return str(e)

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
            temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name, include_dim=list(groupby_agg.keys()))
            response = self.groupby(temp_df,dimension_name,groupby_agg, groupby_agg_key)
            # key = dimension_name+"_"+groupby_agg_key
            # del(self.group_by_backups[key])
            return response

        except Exception as e:
            return str(e)

    def groupby_size(self, dimension_name, groupby_agg_key):
        '''
            description:
                get groupby size for a groupby on a dimension
            input:
                dimension_name <string>:
                groupby_agg_key <string>:
            return:
                size of the groupby
        '''
        try:
            key = dimension_name+"_"+groupby_agg_key
            if(key not in self.group_by_backups):
                res = "groupby not intialized"
            else:
                temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name, include_dim=list(groupby_agg.keys()))
                self.groupby(temp_df,dimension_name,groupby_agg, groupby_agg_key)
                res = str(len(self.group_by_backups[key]))
            # del(self.group_by_backups[key])
            return res

        except Exception as e:
            return str(e)

    def groupby_filterOrder(self, dimension_name, groupby_agg, groupby_agg_key, sort_order, num_rows, sort_column):
        '''
            description:
                get groupby values by a filterOrder(all, top(n), bottom(n)) for a groupby on a dimension
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
                res = "groupby not intialized"#+sort_order+key+"/"+str(list(self.group_by_backups.keys()))
            else:
                #removing the cumulative filters on the current dimension for the groupby
                temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name,include_dim=list(groupby_agg.keys()))
                self.groupby(temp_df,dimension_name,groupby_agg,groupby_agg_key)
                if 'all' == sort_order:
                    temp_df = self.group_by_backups[key].to_pandas().to_dict()
                else:
                    # if len(group_by_backups[key]) == 0:
                    max_rows = max(len(self.group_by_backups[key])-1,0)
                    n_rows = min(num_rows,max_rows)
                    # print("number of rows processed",n_rows)
                    try:
                        if 'top' == sort_order:
                            temp_df = self.group_by_backups[key].nlargest(n_rows,[sort_column]).to_pandas().to_dict()
                        elif 'bottom' == sort_order:
                            temp_df = self.group_by_backups[key].nsmallest(n_rows,[sort_column]).to_pandas().to_dict()
                    except Exception as e:
                        del(self.data_gpu)
                        del(self.back_up_dimension)
                        print("******** oom error **********")
                        return 'oom error, please reload'
                # del(self.group_by_backups[key])
                res = str(self.parse_dict(temp_df))
            return res

        except Exception as e:
            return str(e)

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
            return str(e)

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
            return str(e)


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
            max_min_tuple = (float(self.data_gpu[dimension_name].max()), float(self.data_gpu[dimension_name].min()))
            return str(max_min_tuple)

        except Exception as e:
            return str(e)

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
            # start = time.time()
            status = "not here"
            status += str(self.dimensions_filters.keys())
            if len(self.dimensions_filters.keys()) == 0 or (dimension_name not in self.dimensions_filters) or (dimension_name in self.dimensions_filters and self.dimensions_filters[dimension_name] == ''):
                status = 'in here'
                return str(self.hist_numba_GPU(self.data_gpu[str(dimension_name)].to_gpu_array(),num_of_bins)),status
            else:
                temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name, include_dim = [dimension_name])
                # reset_filters_time = time.time() - start
                return str(self.hist_numba_GPU(temp_df[str(dimension_name)].to_gpu_array(),num_of_bins)), status#+":::"+str(reset_filters_time)

        except Exception as e:
            return str(e),status


    def dimension_filterOrder(self, dimension_name, sort_order, num_rows, columns):
        '''
            description:
                get columns values by a filterOrder(all, top(n), bottom(n)) sorted by dimension_name
            Get parameters:
                dimension_name (string)
                sort_order (string): top/bottom/all
                num_rows (integer): OPTIONAL -> if sort_order= top/bottom
                columns (string): comma separated column names
            Response:
                string(json) -> "{col_1:[__row_values__], col_2:[__row_values__],...}"
        '''
        # print(args)
        # print(columns)
        try:
            columns = columns.split(',')
            if(len(columns) == 0 or columns[0]==''):
                columns = list(self.data_gpu.columns)
            elif dimension_name not in columns:
                columns.append(dimension_name)
            print("requested columns",columns)
            print("available columns",self.data_gpu.columns)

            if 'all' == sort_order:
                temp_df = self.data_gpu.loc[:,list(columns)].to_pandas().to_dict()
            else:
                num_rows = int(num_rows)
                max_rows = max(len(self.data_gpu)-1,0)
                n_rows = min(num_rows, max_rows)
                try:
                    if 'top' == sort_order:
                        # status = 'here in top'
                        temp_df = self.data_gpu.loc[:,list(columns)].nlargest(n_rows,[dimension_name]).to_pandas().to_dict()
                        # status += ' and now temp_df is calculated'
                        # status += str(temp_df)
                    elif 'bottom' == sort_order:
                        # status = 'here in bottom'
                        temp_df = self.data_gpu.loc[:,list(columns)].nsmallest(n_rows,[dimension_name]).to_pandas().to_dict()
                except Exception as e:
                    del(self.data_gpu)
                    del(self.back_up_dimension)
                    print("******** oom error **********")
                    return 'oom error, please reload'+str(e)

            return str(self.parse_dict(temp_df))

        except Exception as e:
            print(e)
            return str(e)

    def dimension_filter(self, dimension_name, comparison_operation, value):
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
                del(self.data_gpu)
                del(self.back_up_dimension)
                print("******** oom error **********")
                return 'oom error, please reload'
            return str(len(self.data_gpu))

        except Exception as e:
            return str(e)

    def dimension_filter_range(self, dimension_name, min_value, max_value):
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
            query = dimension_name+">="+min_value+" and "+dimension_name+"<="+max_value
            # print(str(query))
            if dimension_name in self.dimensions_filters:
                if len(self.dimensions_filters[dimension_name])>0:
                    self.dimensions_filters[dimension_name] += ' and '+ query
                else:
                    self.dimensions_filters[dimension_name] = query
                self.dimensions_filters_response_format[dimension_name] = [min_value,max_value]
            try:
                self.data_gpu = self.data_gpu.query(query)
            except Exception as e:
                del(self.data_gpu)
                del(self.back_up_dimension)
                print("******** oom error **********")
                return 'oom error, please reload'
            return str(len(self.data_gpu))

        except Exception as e:
            return str(e)
