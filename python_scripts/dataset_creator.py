import pyarrow as pa

from pygdf.dataframe import DataFrame

import pandas as pd
import json
import numpy as np
from python_scripts.numbaHistinMem import numba_gpu_histogram

def readArrowToDF(source):
    reader = pa.RecordBatchStreamReader(source)
    pa_df = reader.read_all()
    return pa_df.to_pandas()

def arrowToDisk(df, destination):
    pa_df = pa.RecordBatch.from_pandas(df)
    path = destination+".arrow"
    file = open(path, 'wb')
    writer = pa.ipc.RecordBatchStreamWriter(file, pa_df.schema)
    writer.write_batch(pa_df)
    writer.close()
    file.close()

def process(df,num_of_replicas, name, num_rows = 0):
    df_final = df.append([df]*num_of_replicas, ignore_index=True)
    if num_rows == 0:
        print(len(df_final))
        arrowToDisk(df_final,name)
    else:
        df_final = df_final.loc[0:num_rows]
        print(len(df_final))
        arrowToDisk(df_final,name)
        
    
df = readArrowToDF("uber-dataset-v2.arrow")


uber_1_col = pd.DataFrame(df[['mean_travel_time']], dtype=np.float32)
process(uber_1_col, 16, 'uber-1-col-nonfilter') #create 800M row dataset
process(uber_1_col, 4, 'uber-1-col') #create 240M row dataset

del(uber_1_col)

uber_2_col = pd.DataFrame(df[['mean_travel_time','hod']], dtype=np.float32)
process(uber_2_col, 3, 'uber-2-col') #create 190M row dataset
del(uber_2_col)


uber_3_col = pd.DataFrame(df[['mean_travel_time','hod','standard_deviation_travel_time']], dtype=np.float32)
process(uber_3_col, 3, 'uber-3-col', 150623895) #create 150M row dataset
del(uber_3_col)

uber_4_col = pd.DataFrame(df[['mean_travel_time','hod','standard_deviation_travel_time','geometric_mean_travel_time']], dtype=np.float32)
process(uber_4_col, 3, 'uber-4-col',130623895)
del(uber_4_col)

uber_5_col = pd.DataFrame(df[['mean_travel_time','hod','standard_deviation_travel_time','geometric_mean_travel_time','geometric_standard_deviation_travel_time']], dtype=np.float32)
process(uber_5_col, 3, 'uber-5-col',110623895)
del(uber_5_col)

uber_6_col = pd.DataFrame(df[['mean_travel_time','hod','source_lat','source_long','dst_lat','dst_long']], dtype=np.float32)
process(uber_6_col, 3, 'uber-6-col',100000000)