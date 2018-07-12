import sys, json, numpy as np, pandas as pd, pyarrow as pa

#Custom package
from numbaHist import numba_gpu_histogram


def histNumbaGPU(data,colName):
    '''
        description:
            Calculate histogram leveraging gpu via pycuda(using numba jit)
        input:
            data: pandas df, colName: column name
        Output:
            json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
    '''
    bins = data.shape[0] > 64 and 64 or data.shape[0]
    df1 = numba_gpu_histogram(np.asarray(data[colName]),bins)
    
    dict_temp ={}
    dict_temp['A'] = list(df1[1].astype(str))
    dict_temp['B'] = list(df1[0].astype(str))
        
    print(json.dumps(dict_temp))
    
    sys.stdout.flush()

def histNumpyCPU(data,colName):
    '''
        description:
            Calculate histogram numpy
        input:
            data: pandas df, colName: column name
        Output:
            json -> {A:[__values_of_colName_with_max_64_bins__], B:[__frequencies_per_bin__]}
    '''
    bins = data.shape[0] > 64 and 64 or data.shape[0]
    df1 = np.histogram(data[colName],bins=bins)
    dict_temp ={}
    
    dict_temp['A'] = list(df1[1].astype(str))
    dict_temp['B'] = list(df1[0].astype(str))
    
    print(json.dumps(dict_temp))
    sys.stdout.flush()

def getColumns(data):
    '''
        description:
        Column names in a data frame
        input:
            data: pandas df
        Output:
            list of column names
    '''
    print(list(data.columns))
    sys.stdout.flush()

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
    reader = pa.RecordBatchStreamReader(source)
    pa_df = reader.read_all()
    return pa_df.to_pandas()

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

def getHist(data, processing,colName):
    '''
        description:
            Get Histogram as per the specified processing type
        input:
            processing: numba or numpy
            data: pandas df
            colName: column name
    '''
    if processing == 'numba':
        histNumbaGPU(data,colName)
    elif processing == 'numpy':
        histNumpyCPU(data,colName)

def main():
    '''
        description:
            1. get Histogram as per the specified processing type and file load type
            2. get Columns names as per the specified file load type
        
        input:
            command line args:
                python script.py sessID file type processing load_type columnName
            args:
                sessID: sessionID to uniquely identify and serve multiple sessions(yet to be implemented)
                file: file path
                type: hist or columns
                processing: numpy or numba
                load_type: csv or arrow
                columnName: (only when type=hist) columnName when type of request is hist
    '''
    file, type, processing, load_type = sys.argv[2:6] or ''
    data = readData(load_type,file)
    
    if type == 'hist':
        getHist(data, processing,sys.argv[-1])
    elif type == 'columns':
        getColumns(data)

    

#start process
if __name__ == '__main__':
    main()
