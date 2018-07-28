from pyarrow import RecordBatchStreamReader
from numbaHistinMem import numba_gpu_histogram
from pygdf.dataframe import DataFrame
import json
import os

data_gpu = None

def hist_numba_GPU(data,colName,bins):
    '''
        description:
            Calculate histogram leveraging gpu via pycuda(using numba jit)
        input:
            data: pandas df, colName: column name
        Output:
            json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
    '''
    # bins = 500#data.transpose().shape[0] > 500 and 500 or data.transpose().shape[0]
    df1 = numba_gpu_histogram(data,int(bins))
    # df1 = numba_gpu_histogram(data[colName],bins)
    dict_temp ={}
    
    dict_temp['X'] = list(df1[1].astype(str))
    dict_temp['Y'] = list(df1[0].astype(str))
    
    return str(json.dumps(dict_temp))

def get_hist(data, processing,colName,bins):
    '''
        description:
            Get Histogram as per the specified processing type
        input:
            processing: numba or numpy
            data: pandas df
            colName: column name
    '''
    if processing == 'numba':
        return hist_numba_GPU(data,colName,bins)
    # elif processing == 'numpy':
    #     return histNumpyCPU(data,colName,bins)

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
    # sys.stdout.flush()

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
    # if load_type == 'csv':
    #     data = readCSV(file)
    # elif load_type == 'arrow':
    #     data = read_arrow_to_DF(file)
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
    global data_gpu
    res = input_from_client
    try:
        if input_from_client == "exit":
            os._exit(1)
        
        elif 'read' in input_from_client:
            #calling to precompile jit functions
            data_gpu = read_data("arrow",input_from_client.split(":::")[1])
            # hist_numba_GPU(data_gpu,0,64)

            #warm up function for the cuda-jit
            hist_numba_GPU(data_gpu[data_gpu.columns[0]].to_gpu_array(),0,64)
            res = "data read successfully"
        
        elif data_gpu is not None:
            if 'columns' in input_from_client:
                res = str(get_columns(data_gpu))
            
            elif 'hist' in input_from_client:
                args_hist = input_from_client.split(":::")
                res = str(get_hist(data_gpu[str(args_hist[3])].to_gpu_array(),args_hist[2],0, args_hist[4]))
                
            elif 'filterOrder' in input_from_client:
                args_hist = input_from_client.split(":::")
                if 'top' == args_hist[1]:
                    temp_df = data_gpu.nlargest(int(args_hist[5]),[args_hist[4]]).to_pandas().to_dict()
                elif 'bottom' == args_hist[1]:
                        temp_df = data_gpu.nsmallest(int(args_hist[5]),[args_hist[4]]).to_pandas().to_dict()                               
                print(temp_df)
                res = str(df_to_dict(temp_df))
                
            elif 'get_max_min' in input_from_client:
                args_hist = input_from_client.split(":::")
                max_min_tuple = float(data_gpu[args_hist[2]].max()), float(data_gpu[args_hist[2]].max())
                res = str(max_min_tuple)

            elif input_from_client == "size":
                    res = str(get_size(data_gpu))
        else:
            res = "first read some data :-P"
        
        print("Result of processing {} is: {}".format(input_from_client, res))
        
    except Exception as e:
        res= str(e)
        print("some error occured",e)
    
    return res