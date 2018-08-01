from pyarrow import RecordBatchStreamReader
from numbaHistinMem import numba_gpu_histogram
from pygdf.dataframe import DataFrame
import json
import os

data_gpu = None
back_up_dimension = None
dimensions_filters = {}

def hist_numba_GPU(data,bins):
    '''
        description:
            Calculate histogram leveraging gpu via pycuda(using numba jit)
        input:
            data: pygdf row as a series -> gpu mem pointer, bins: column name
        Output:
            json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
    '''
    df1 = numba_gpu_histogram(data,int(bins))
    dict_temp ={}
    
    dict_temp['X'] = list(df1[1].astype(str))
    dict_temp['Y'] = list(df1[0].astype(str))
    
    return str(json.dumps(dict_temp))


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

def df_to_dict(data):
    '''
        description:
            get parse string format of the dataframe, that can be sent to the socket-client
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

def reset_filters():
    '''
        description:
            reset filters on the data_gpu dataframe by executing all filters in the dimension_filters dictionary
    '''
    global data_gpu, dimensions_filters
    print("inside reset filters")
    print(dimensions_filters)
    temp_list = []
    for key in dimensions_filters.keys():
        temp_list = temp_list + dimensions_filters[key]
    query = ' and '.join(temp_list)
    print(query)
    if(len(query) >0):
        data_gpu = data_gpu.query(query)

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
    global data_gpu, back_up_dimension, dimensions_filters
    res = ''
    print(dimensions_filters)
    try:
        args = input_from_client.split(":::")
        # print(args)
        if  "exit" == args[0]:
            os._exit(1)
        
        elif 'read' == args[0]:
            data_gpu = read_data("arrow",args[1])
            back_up_dimension = data_gpu
            #warm up function for the cuda-jit
            hist_numba_GPU(data_gpu[data_gpu.columns[0]].to_gpu_array(),64)
            res = "data read successfully"
    
        elif 'schema' == args[0]:
            res = str(get_columns(data_gpu))

        elif "size" == args[0]:
            res = str(get_size(data_gpu))

        elif 'dimension' in args[0]:
            if 'dimension_load' == args[0]:
                if args[1] not in dimensions_filters:
                    dimensions_filters[args[1]] = []
                    res = 'dimension loaded successfully'
                else:
                    res = 'dimension already exists'

            elif 'dimension_reset' == args[0]:
                #reseting the cumulative filters on the current dimension
                data_gpu = back_up_dimension
                dimensions_filters[args[1]] = []
                reset_filters()
                res = str(len(data_gpu))

            elif 'dimension_get_max_min' == args[0]:
                max_min_tuple = float(data_gpu[args[1]].max()), float(data_gpu[args[1]].min())
                res = str(max_min_tuple)
            
            elif 'dimension_hist' == args[0]:
                res = str(numba_gpu_histogram(data_gpu[str(args[1])].to_gpu_array(),args))

            elif 'dimension_filterOrder' == args[0]:
                n_rows = min(int(args[-1]), len(data_gpu)) - 1
                if 'top' == args[1]:
                    temp_df = data_gpu.nlargest(n_rows,[args[-2]]).to_pandas().to_dict()
                elif 'bottom' == args[1]:
                    temp_df = data_gpu.nsmallest(n_rows,[args[-2]]).to_pandas().to_dict()                               
                print(temp_df)
                res = str(df_to_dict(temp_df))

            elif 'dimension_filter' == args[0]:
                query = args[1]+args[2]+args[3]
                if args[1] in dimensions_filters:
                    dimensions_filters[args[1]].append(query)
                data_gpu = data_gpu.query(query)
                res = str(len(data_gpu))
        else:
            res = "first read some data :-P"
        
        print("Result of processing {} is: {}".format(input_from_client, res))
        
    except Exception as e:
        res= str(e)
        print("some error occured",e)
    
    return res