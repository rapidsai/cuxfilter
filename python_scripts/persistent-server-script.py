# server.py
import socket,sys,json
import numpy as np, pandas as pd, pyarrow as pa
from numbaHistinMem import numba_gpu_histogram
from numba import cuda
import time
from pygdf.dataframe import DataFrame

def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    try:
        while True:

            # the input is in bytes, so decode it
            input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

            # MAX_BUFFER_SIZE is how big the message can be
            # this is test if it's sufficiently big
            siz = sys.getsizeof(input_from_client_bytes)
            if  siz >= MAX_BUFFER_SIZE:
                print("The length of input is probably too long: {}".format(siz))

            # decode input and strip the end of line
            start_time = time.perf_counter()

            input_from_client_all = input_from_client_bytes.decode("utf8").rstrip()
            input_from_client_all = input_from_client_all.split("////")
            for input_from_client in input_from_client_all:
                try:
                    if input_from_client == "exit":
                        sys.exit()
                    elif 'read' in input_from_client:
                        data_gpu = readData("arrow",input_from_client.split(":::")[1])
                        # numba_gpu_histogram(data_df_final[data_df_final.columns[0]],64)
                        # data_gpu = cuda.to_device(np.asarray(data_df_final).transpose())
                        #calling to precompile jit functions
                        # histNumbaGPU(data_gpu,0,64)
                        histNumbaGPU(data_gpu[data_gpu.columns[0]].to_gpu_array(),0,64)
                        
                        res = "data read successfully:::Dataset Size: "+str(len(data_gpu)/1000000)+" Million rows \n"
                    elif 'columns' in input_from_client:
                        if 'data_gpu' in locals():
                            res = str(getColumns(data_gpu))
                        else:
                            res = "first read some data :-P"
                    elif 'hist' in input_from_client:
                        # print("calculating histogram")
                        args_hist = input_from_client.split(":::")
                        # print(args_hist)
                        if 'data_gpu' in locals():
                            # print("inside if condition, definitely works")
                            res = str(getHist(data_gpu[str(args_hist[3])].to_gpu_array(),args_hist[2],0, args_hist[4]))
                            # res = str(getHist(data_df_final,args_hist[2],args_hist[3]))
                        else:
                            res = "first read some data :-P"
                    print("Result of processing {} is: {}".format(input_from_client, res))
                except Exception as e:
                    res= str(e)
                    print("some error occured", res)
                    
                elapsed = time.perf_counter() - start_time
                
                
                res = res+":::"+str(elapsed)
                vysl = res.encode("utf8")  # encode the result string
                conn.sendall(vysl)  # send it to client
    except ConnectionAbortedError:
        conn.close()  # close connection
    print('Connection ' + ip + ':' + port + " ended")

def start_server():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("0.0.0.0", 3001))
        print('Socket bind complete')
    except (ConnectionResetError,socket.error) as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    soc.listen(10)
    print('Socket now listening')

    # for handling task in separate jobs we need threading
    from threading import Thread

    # this will make an infinite loop needed for 
    # not reseting server for every client
    # a = True
    threads = []
    # while True:
    try:
        conn, addr = soc.accept()
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            threads.append(Thread(target=client_thread, args=(conn, ip, port)))
            threads[-1].start()
        except:
            print("Terible error!")
            import traceback
            traceback.print_exc()
            # break
    except KeyboardInterrupt:
        if soc:  # <---
            soc.close()
        # break
    for t in threads:
        print("thread is alive?: ",t.is_alive())
    soc.close()

def histNumbaGPU(data,colName,bins):
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
    
    dict_temp['A'] = list(df1[1].astype(str))
    dict_temp['B'] = list(df1[0].astype(str))
    
    return str(json.dumps(dict_temp))

def histNumpyCPU(data,colName,bins):
    '''
        description:
            Calculate histogram numpy
        input:
            data: pandas df, colName: column name
        Output:
            json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
    '''
    # bins = data.shape[0] > 64 and 64 or data.shape[0]
    df1 = np.histogram(data[colName],bins=bins)
    dict_temp ={}
    
    dict_temp['A'] = list(df1[1].astype(str))
    dict_temp['B'] = list(df1[0].astype(str))
    print(str(json.dumps(dict_temp)))
    return json.dumps(dict_temp)

def getHist(data, processing,colName,bins):
    '''
        description:
            Get Histogram as per the specified processing type
        input:
            processing: numba or numpy
            data: pandas df
            colName: column name
    '''
    if processing == 'numba':
        return histNumbaGPU(data,colName,bins)
    elif processing == 'numpy':
        return histNumpyCPU(data,colName,bins)

def getColumns(data):
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

def readArrowToDF(source):
    '''
        description:
            Read arrow file from disk using apache pyarrow
        input:
            source: file path
        return:
            pandas dataframe
    '''
    source = source+".arrow"
    pa_df = pa.RecordBatchStreamReader(source).read_all().to_pandas()
    return DataFrame.from_pandas(pa_df)

def readCSV(source):
    '''
        description:
            Read csv file from disk using pandas
        input:
            source: file path
        return:
            pandas dataframe
    '''
    df = pd.read_csv(source)
    return df

def readData(load_type,file):
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
    if load_type == 'csv':
        data = readCSV(file)
    elif load_type == 'arrow':
        data = readArrowToDF(file)
    return data

if __name__ == '__main__':
    start_server()
