from pyarrow import RecordBatchStreamReader
from numbaHistinMem import numba_gpu_histogram
from pygdf.dataframe import DataFrame
import json
import os

data_gpu = None
back_up_dimension = None
dimensions_filters = {}
group_by_backups = {}

def hist_numba_GPU(data,bins):
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

def groupby(data,column_name, groupby_agg,groupby_agg_key):
    '''
        description:
            Calculate groupby on a given column on the pygdf 
        input:
            data: pygdf row as a series -> gpu mem pointer, 
            column_name: column name
        Output:
            json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
    '''
    global group_by_backups
    print(column_name)
    print("inside groupby function")
    group_appl = data.groupby(by=[column_name]).agg(groupby_agg)
    print(len(group_appl))
    key = column_name+"_"+groupby_agg_key
    group_by_backups[key] = group_appl  #.loc[:,[column_name,column_name+'_'+agg]]
    return "groupby intialized successfully"

def get_columns(data):
    '''
        description:
        Column names in a data frame
        input:
            data: pandas df
        Output:
            list of column names
    '''
    return list(data.columns)

def read_arrow_to_DF(source):
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
    return DataFrame.from_pandas(pa_df)



def read_data(load_type,file):
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
    file = str("uploads/"+file)
    data = read_arrow_to_DF(file)
    return data

def parse_dict(data):
    '''
        description:
            get parsed string format of the dictionary, that can be sent to the socket-client
        input:
            data: dataframe
        return:
            shape string
    '''
    temp_dict = {}
    for i in data:
        temp_dict[i] = list(data[i].values())
    return json.dumps(temp_dict)

def get_size(data):
    '''
        description:
            get shape of the dataframe
        input:
            data: dataframe
        return:
            shape tuple
    '''
    return (len(data),len(data.columns))

def reset_filters(data, omit=None):
    '''
        description:
            reset filters on the data_gpu dataframe by executing all filters in the dimension_filters dictionary
    '''
    global dimensions_filters
    print("inside reset filters")
    print(dimensions_filters)
    temp_list = []
    for key in dimensions_filters.keys():
        if omit is not None and omit == key:
            continue
        temp_list = temp_list + dimensions_filters[key]
    query = ' and '.join(temp_list)
    if(len(query) >0):
        return data.query(query)
    else:
        print(len(data))
        return data

def process_input_from_client(input_from_client):
    '''
        description:
            get input from socket-client, parse it, and execute the request and send the response
        input:
            input_from_client: string with ':::' as separator between different arguments of the request
        return:
            res: response string
        global:
            data_gpu: pointer to dataset stored in gpu_mem, global in the context of this thread of server serving the socket-client
    '''
    global data_gpu, back_up_dimension, dimensions_filters, group_by_backups
    res = ''
    main_command = ''
    # print(dimensions_filters)
    try:
        args = input_from_client.split(":::")
        main_command = args[0]
        if  "exit" == main_command:
            os._exit(1)
        
        elif 'read' == main_command:
            dataset_name = args[1]
            data_gpu = read_data("arrow",dataset_name)
            back_up_dimension = data_gpu
            #warm up function for the cuda-jit
            hist_numba_GPU(data_gpu[data_gpu.columns[4]].to_gpu_array(),640)
            res = "data read successfully"
    
        elif 'schema' == main_command:
            res = str(get_columns(data_gpu))

        elif "size" == main_command:
            res = str(get_size(data_gpu))

        elif 'groupby' in main_command:
            # print("groupby operations")
            dimension_name =args[1]
            groupby_agg = json.loads(args[-1])
            groupby_agg_key = ':'.join(list(groupby_agg.keys())+list(groupby_agg.values())[0])

            if 'groupby_load' == main_command:
                #removing the cumulative filters on the current dimension for the groupby
                temp_df = reset_filters(back_up_dimension, omit=dimension_name)
                res = groupby(temp_df,dimension_name,groupby_agg, groupby_agg_key)
            
            elif 'groupby_size' == main_command:
                key = dimension_name+"_"+groupby_agg_key
                if(key not in group_by_backups):
                    res = "groupby not intialized"
                else:
                    #removing the cumulative filters on the current dimension for the groupby
                    temp_df = reset_filters(back_up_dimension, omit=dimension_name)
                    groupby(temp_df,dimension_name,groupby_agg,groupby_agg_key)
                    res = str(len(group_by_backups[key]))
            
            elif 'groupby_filterOrder' == main_command:
                sort_order = args[2]
                key = dimension_name+"_"+groupby_agg_key
                print(args)
                print(key)
                print(group_by_backups.keys())
                if(key not in group_by_backups):
                    res = "groupby not intialized"
                else:
                    #removing the cumulative filters on the current dimension for the groupby
                    temp_df = reset_filters(back_up_dimension, omit=dimension_name)
                    groupby(temp_df,dimension_name,groupby_agg,groupby_agg_key)

                    if 'all' == sort_order:
                        temp_df = group_by_backups[key].to_pandas().to_dict()
                    else:
                        sort_column = args[4]
                        num_rows = int(args[3])
                        n_rows = min(num_rows, len(group_by_backups[key])) - 1
                        if 'top' == sort_order:
                            temp_df = group_by_backups[key].nlargest(n_rows,[sort_column]).to_pandas().to_dict()
                        elif 'bottom' == sort_order:
                            temp_df = group_by_backups[key].nsmallest(n_rows,[sort_column]).to_pandas().to_dict()
                    res = str(parse_dict(temp_df))

        elif 'dimension' in main_command:
            dimension_name = args[1]

            if 'dimension_load' == main_command:
                if dimension_name not in dimensions_filters:
                    dimensions_filters[dimension_name] = []
                    res = 'dimension loaded successfully'
                else:
                    res = 'dimension already exists'

            elif 'dimension_reset' == main_command:
                #reseting the cumulative filters on the current dimension
                data_gpu = back_up_dimension
                dimensions_filters[dimension_name] = []
                data_gpu = reset_filters(data_gpu)
                res = str(len(data_gpu))

            elif 'dimension_get_max_min' == main_command:
                max_min_tuple = float(data_gpu[dimension_name].max()), float(data_gpu[dimension_name].min())
                res = str(max_min_tuple)
            
            elif 'dimension_hist' == main_command:
                num_of_bins = int(args[2])
                temp_df = reset_filters(back_up_dimension, omit=dimension_name)
                res = str(hist_numba_GPU(temp_df[str(dimension_name)].to_gpu_array(),num_of_bins))

            elif 'dimension_filterOrder' == main_command:
                sort_order = args[2]
                print(args)
                columns = args[4].split(',')
                print(columns)

                if(len(columns) == 0):
                    columns = data_gpu.columns
                elif dimension_name not in columns:
                    columns.append(dimension_name)
                    
                if 'all' == sort_order:
                    temp_df = data_gpu.loc[:,columns].to_pandas().to_dict()
                else:
                    num_rows = int(args[3])
                    n_rows = min(num_rows, len(data_gpu)) - 1
                    if 'top' == sort_order:
                        temp_df = data_gpu.loc[:,columns].nlargest(n_rows,[dimension_name]).to_pandas().to_dict()
                    elif 'bottom' == sort_order:
                        temp_df = data_gpu.loc[:,columns].nsmallest(n_rows,[dimension_name]).to_pandas().to_dict()
                                             
                res = str(parse_dict(temp_df))

            elif 'dimension_filter' == main_command:
                comparison_operation = args[2]
                value = args[3]
                query = dimension_name+comparison_operation+value
                if dimension_name in dimensions_filters:
                    dimensions_filters[dimension_name].append(query)
                data_gpu = data_gpu.query(query)
                res = str(len(data_gpu))
            
            elif 'dimension_filter_range' == main_command:
                min_value = args[2]
                max_value = args[3]
                query = dimension_name+">"+min_value+" and "+dimension_name+"<"+max_value
                print(str(query))
                if dimension_name in dimensions_filters:
                    dimensions_filters[dimension_name].append(query)
                data_gpu = data_gpu.query(query)
                res = str(len(data_gpu))

        else:
            res = "first read some data :-P"
        
        # print("Result of processing {} is: {}".format(input_from_client, res))
        
    except Exception as e:
        res= str("Exception raised: check your input", e)
        print("some error occured",e)
    
    return main_command+":::"+res