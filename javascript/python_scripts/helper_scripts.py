import pandas as pd
import pyarrow as pa
import json, sys, argparse
import numpy as np

def pandas_df_to_arrow(df):
    print('converting arrow dataframe to a pandas df')
    return pa.RecordBatch.from_pandas(df, preserve_index=False)

def read_arrow(source):
    print('reading arrow file as arrow table from disk')
    reader = pa.RecordBatchStreamReader(source)
    pa_df = reader.read_all()
    return pa_df

def read_arrow_as_pandas(source):
    print('reading arrow file as pandas dataframe from disk')
    reader = pa.RecordBatchStreamReader(source)
    pa_df = reader.read_all()
    return pa_df.to_pandas()

def write_arrow_to_disk(arrow_df, path):
    print('saving as an arrow file on the path specified:', path.split('.')[0])
    path = path.split('.')[0]+".arrow"
    file = open(path, 'wb')
    writer = pa.ipc.RecordBatchStreamWriter(file, arrow_df.schema)
    writer.write_batch(arrow_df)
    writer.close()
    file.close()

def write_csv_to_disk(pandas_df, path):
    print('saving as a csv file on the path specified:', path.split('.')[0])
    path = path.split('.')[0]+".csv"
    pandas_df.to_csv(path, index=False)

def csv_to_arrow(source):
    print('conversion from csv to arrow started')
    try:
        print('reading csv...')
        data = pd.read_csv(source,dtype=np.float32)
        write_arrow_to_disk(pandas_df_to_arrow(data), source)
        print("file successfully converted to an arrow format")
    except Exception as e:
        print("error:",e)

def arrow_to_csv(source):
    print('conversion from arrow to csv started')
    try:
        data = read_arrow_as_pandas(source)
        write_csv_to_disk(data, source)
        print("file successfully converted to an csv format")
    except Exception as e:
        print("error:",e)

def generate_random_dataset(num_rows,num_columns,type,range_min,range_max, destination):
    print('generating random dataset of type', type)
    cols = []
    for i in range(num_columns):
        cols.append("col-"+i)
    a = np.random.rand(range_min,range_max,(int(num_rows),int(num_columns)))
    path = destination+"data-"+str(int(int(num_rows)/1000))+"k"
    df = pd.DataFrame(a,columns=cols)
    if type == 'csv':
        write_csv_to_disk(df, path)
    else:
        write_arrow_to_disk(df, path)
    print("file saved to ",path)

def get_parser_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fn', help= 'type of function', type=str)
    parser.add_argument('--num_rows', help = 'number of rows(random dataset generation)', default = 1000, type=int)
    parser.add_argument('--num_columns', help = 'number of columns(random dataset generation)', default = 2, type=int)
    parser.add_argument('--destination_type', help = 'destination type(csv/arrow) of dataset to be generated', default = 'arrow', type=str)
    parser.add_argument('--range_min', help = 'random dataset - min value',default = 1.0, type=float)
    parser.add_argument('--range_max', help = 'random dataset - max value',default = 1000.0, type=float)
    parser.add_argument('--destination', help = 'destination path', default = '.', type=str)
    parser.add_argument('--source', help = 'source file path', type=str)
    return parser

def process_args(args):
    if args.fn == 'csv_to_arrow':
            csv_to_arrow(args.source)
    elif args.fn == 'generate_random_dataset':
            generate_random_dataset(args.num_rows,args.num_columns,args.destination_type, args.range_min, args.range_max, args.destination)
    elif args.fn == 'arrow_to_csv':
            arrow_to_csv(args.source)

#start process
if __name__ == '__main__':
    parser = get_parser_config()
    args = parser.parse_args()
    process_args(args)
