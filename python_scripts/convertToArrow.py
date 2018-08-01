import pandas as pd, pyarrow as pa, json, sys, numpy as np

def csvToArrow(path):
    data = pd.read_csv(path,dtype=np.float32)
    pa_df = pa.RecordBatch.from_pandas(data)
    path = path+".arrow"
    file = open(path, 'wb')
    writer = pa.ipc.RecordBatchStreamWriter(file, pa_df.schema)
    writer.write_batch(pa_df)
    writer.close()
    file.close()

def main():
    #get our data as an array from read_in()    
    sessId = sys.argv[1]

    with open('../data/data.json', 'r') as f:
        datastore = json.loads(f.read())
    
    csvToArrow(datastore['path'])
    


#start process
if __name__ == '__main__':
    main()