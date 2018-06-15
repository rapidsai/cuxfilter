## compute_input.py

import sys, json, numpy as np, pandas as pd


def main():
    #get our data as an array from read_in()    
    sessId = sys.argv[1]
    with open('data/data.json', 'r') as f:
        datastore = json.loads(f.read())
    
    file = datastore['path']
    
    data = pd.read_csv(file, encoding = "ISO-8859-1")
    print(data.head(5))

    

#start process
if __name__ == '__main__':
    main()