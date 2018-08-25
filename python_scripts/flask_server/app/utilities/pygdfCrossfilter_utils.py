from pyarrow import RecordBatchStreamReader
from app.utilities.numbaHistinMem import numba_gpu_histogram
from pygdf.dataframe import DataFrame
import json
import os
import numpy as np
import time
import sys


class pygdfCrossfilter_utils:
    data_gpu = None
    back_up_dimension = None
    dimensions_filters = {}
    group_by_backups = {}

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
        group_appl = data.groupby(by=[column_name]).agg(groupby_agg)
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
        self.data_gpu = DataFrame.from_pandas(pa_df)
        self.back_up_dimension = self.data_gpu
        return "data read successfully"


    def read_data(self,load_type,file):
        '''
            description:
                Read file as per the load type
            input:
                load_type: csv or arrow
                file: file path
            return:
                pandas dataframe
        '''
        #file is in the uploads/ folder, so append that to the path
        file = str("/usr/src/app/node_server/uploads/"+file)
        data = self.read_arrow_to_DF(file)
        return data

    def default(self,o):
        if isinstance(o, np.int64): return int(o)
        raise TypeError

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
            return json.dumps(temp_dict,default=self.default)
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
                    return data.loc[:,column_list].query(query)
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
            return self.groupby(temp_df,dimension_name,groupby_agg, groupby_agg_key)

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
                res = "groupby not intialized"
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
                    if 'top' == sort_order:
                        temp_df = self.group_by_backups[key].nlargest(n_rows,[sort_column]).to_pandas().to_dict()
                    elif 'bottom' == sort_order:
                        temp_df = self.group_by_backups[key].nsmallest(n_rows,[sort_column]).to_pandas().to_dict()
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
            if len(self.dimensions_filters.keys()) == 0 or (len(self.dimensions_filters.keys()) == 1 and dimension_name in self.dimensions_filters):
                return str(self.hist_numba_GPU(self.data_gpu[str(dimension_name)].to_gpu_array(),num_of_bins))
            else:
                temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name, include_dim = [dimension_name])
                # reset_filters_time = time.time() - start
                return str(self.hist_numba_GPU(temp_df[str(dimension_name)].to_gpu_array(),num_of_bins))#+":::"+str(reset_filters_time)

        except Exception as e:
            return str(e)


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
                temp_df = self.data_gpu.loc[:,columns].to_pandas().to_dict()
            else:
                num_rows = int(num_rows)
                max_rows = max(len(self.data_gpu)-1,0)
                n_rows = min(num_rows, max_rows)
                if 'top' == sort_order:
                    temp_df = self.data_gpu.loc[:,columns].nlargest(n_rows,[dimension_name]).to_pandas().to_dict()
                elif 'bottom' == sort_order:
                    temp_df = self.data_gpu.loc[:,columns].nsmallest(n_rows,[dimension_name]).to_pandas().to_dict()

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
            self.data_gpu = self.data_gpu.query(query)
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
            self.data_gpu = self.data_gpu.query(query)
            return str(len(self.data_gpu))

        except Exception as e:
            return str(e)


    # def process_input_from_client(self, input_from_client):
    #     '''
    #         description:
    #             get input from socket-client, parse it, and execute the request and send the response
    #         input:
    #             input_from_client: string with ':::' as separator between different arguments of the request
    #         return:
    #             res: response string
    #         global:
    #             data_gpu: pointer to dataset stored in gpu_mem, global in the context of this thread of server serving the socket-client
    #     '''
    #     # global data_gpu, back_up_dimension, dimensions_filters, group_by_backups
    #     res = ''
    #     main_command = ''
    #     tcp_header = ''
    #     # print(dimensions_filters)
    #     try:
    #         args = input_from_client.split(":::")
    #         main_command = args[0]
    #         tcp_header = args[0]
    #         if  "exit" == main_command:
    #             sys.exit()
    #
    #         elif 'read' == main_command:
    #             dataset_name = args[1]
    #             res = self.read_data("arrow",dataset_name)
    #             #warm up function for the cuda-jit
    #             self.hist_numba_GPU(self.data_gpu[self.data_gpu.columns[-1]].to_gpu_array(),640)
    #
    #         elif 'schema' == main_command:
    #             res = self.get_columns()
    #
    #         elif "size" == main_command:
    #             res = self.get_size()
    #
    #         elif 'reset_all' == main_command:
    #             res = self.reset_all_filters()
    #
    #         elif 'groupby' in main_command:
    #             # print("groupby operations")
    #             dimension_name = args[1]
    #             tcp_header = tcp_header+dimension_name
    #             groupby_agg = json.loads(args[-1])
    #             groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])
    #
    #             if 'groupby_load' == main_command:
    #                 #removing the cumulative filters on the current dimension for the groupby
    #                 temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name, include_dim=list(groupby_agg.keys()))
    #                 res = self.groupby(temp_df,dimension_name,groupby_agg, groupby_agg_key)
    #
    #             elif 'groupby_size' == main_command:
    #                 key = dimension_name+"_"+groupby_agg_key
    #                 if(key not in self.group_by_backups):
    #                     res = "groupby not intialized"
    #                 else:
    #                     res = str(len(self.group_by_backups[key]))
    #
    #             elif 'groupby_filterOrder' == main_command:
    #                 sort_order = args[2]
    #                 key = dimension_name+"_"+groupby_agg_key
    #                 # print(args)
    #                 # print(key)
    #                 # print(group_by_backups.keys())
    #                 if(key not in self.group_by_backups):
    #                     res = "groupby not intialized"
    #                 else:
    #                     #removing the cumulative filters on the current dimension for the groupby
    #                     temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name,include_dim=list(groupby_agg.keys()))
    #                     self.groupby(temp_df,dimension_name,groupby_agg,groupby_agg_key)
    #                     if 'all' == sort_order:
    #                         temp_df = self.group_by_backups[key].to_pandas().to_dict()
    #                     else:
    #                         sort_column = args[4]
    #                         num_rows = int(args[3])
    #                         # if len(group_by_backups[key]) == 0:
    #                         max_rows = max(len(self.group_by_backups[key])-1,0)
    #                         n_rows = min(num_rows,max_rows)
    #                         # print("number of rows processed",n_rows)
    #                         if 'top' == sort_order:
    #                             temp_df = self.group_by_backups[key].nlargest(n_rows,[sort_column]).to_pandas().to_dict()
    #                         elif 'bottom' == sort_order:
    #                             temp_df = self.group_by_backups[key].nsmallest(n_rows,[sort_column]).to_pandas().to_dict()
    #                     res = str(self.parse_dict(temp_df))
    #
    #         elif 'dimension' in main_command:
    #             dimension_name = args[1]
    #             tcp_header = tcp_header+dimension_name
    #
    #             if 'dimension_load' == main_command:
    #                 if dimension_name not in self.dimensions_filters:
    #                     self.dimensions_filters[dimension_name] = ''
    #                     res = 'dimension loaded successfully'
    #                 else:
    #                     res = 'dimension already exists'
    #
    #             elif 'dimension_reset' == main_command:
    #                 #reseting the cumulative filters on the current dimension
    #                 self.data_gpu = self.back_up_dimension
    #                 self.dimensions_filters[dimension_name] = ''
    #                 self.data_gpu = self.reset_filters(self.data_gpu)
    #                 res = str(len(self.data_gpu))
    #
    #             elif 'dimension_get_max_min' == main_command:
    #                 max_min_tuple = float(self.data_gpu[dimension_name].max()), float(self.data_gpu[dimension_name].min())
    #                 res = str(max_min_tuple)
    #
    #             elif 'dimension_hist' == main_command:
    #                 num_of_bins = int(args[2])
    #                 # start = time.time()
    #                 temp_df = self.reset_filters(self.back_up_dimension, omit=dimension_name, include_dim = [dimension_name])
    #                 # reset_filters_time = time.time() - start
    #                 res = str(self.hist_numba_GPU(temp_df[str(dimension_name)].to_gpu_array(),num_of_bins))#+":::"+str(reset_filters_time)
    #
    #             elif 'dimension_filterOrder' == main_command:
    #                 sort_order = args[2]
    #                 # print(args)
    #                 columns = args[4].split(',')
    #                 # print(columns)
    #
    #                 if(len(columns) == 0 or columns[0]==''):
    #                     columns = list(self.data_gpu.columns)
    #                 elif dimension_name not in columns:
    #                     columns.append(dimension_name)
    #                 print("requested columns",columns)
    #                 print("available columns",self.data_gpu.columns)
    #
    #                 if 'all' == sort_order:
    #                     temp_df = self.data_gpu.loc[:,columns].to_pandas().to_dict()
    #                 else:
    #                     num_rows = int(args[3])
    #                     max_rows = max(len(self.data_gpu)-1,0)
    #                     n_rows = min(num_rows, max_rows)
    #                     if 'top' == sort_order:
    #                         temp_df = self.data_gpu.loc[:,columns].nlargest(n_rows,[dimension_name]).to_pandas().to_dict()
    #                     elif 'bottom' == sort_order:
    #                         temp_df = self.data_gpu.loc[:,columns].nsmallest(n_rows,[dimension_name]).to_pandas().to_dict()
    #
    #                 res = str(self.parse_dict(temp_df))
    #
    #             elif 'dimension_filter' == main_command:
    #                 comparison_operation = args[2]
    #                 value = args[3]
    #                 query = dimension_name+comparison_operation+value
    #                 if dimension_name in self.dimensions_filters:
    #                     if len(self.dimensions_filters[dimension_name])>0:
    #                         self.dimensions_filters[dimension_name] += ' and '+ query
    #                     else:
    #                         self.dimensions_filters[dimension_name] = query
    #                 self.data_gpu = self.data_gpu.query(query)
    #                 res = str(len(self.data_gpu))
    #
    #             elif 'dimension_filter_range' == main_command:
    #                 min_value = args[2]
    #                 max_value = args[3]
    #                 query = dimension_name+">"+min_value+" and "+dimension_name+"<"+max_value
    #                 # print(str(query))
    #                 if dimension_name in self.dimensions_filters:
    #                     if len(self.dimensions_filters[dimension_name])>0:
    #                         self.dimensions_filters[dimension_name] += ' and '+ query
    #                     else:
    #                         self.dimensions_filters[dimension_name] = query
    #                 self.data_gpu = self.data_gpu.query(query)
    #                 res = str(len(self.data_gpu))
    #
    #         else:
    #             res = "first read some data :-P"
    #
    #         # print("Result of processing {} is: {}".format(input_from_client, res))
    #
    #     except Exception as e:
    #         res= str("Exception raised: check your input", e)
    #         print("some error occured",e)
    #
    #     return tcp_header+":::"+res
