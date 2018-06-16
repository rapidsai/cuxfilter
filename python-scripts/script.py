## compute_input.py

import sys, json, numpy as np, pandas as pd


def main():
    #get our data as an array from read_in()    
    sessId = sys.argv[1]
    with open('data/data.json', 'r') as f:
        datastore = json.loads(f.read())
    
    file = datastore['path']
    
    data = pd.read_csv(file)
    df1 = data['A'].value_counts()

    dict_temp ={}

    dict_temp['A'] = df1.index

    dict_temp['B'] = df1.values

    file_name = 'user_data/'+file.split('\\')[1] +"data.json"
    
    pd.DataFrame(dict_temp).to_json(file_name, orient='index')

    

#start process
if __name__ == '__main__':
    main()