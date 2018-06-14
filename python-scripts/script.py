## compute_input.py

import sys, json, numpy as np, pandas as pd

#Read data from stdin
def read_in():
    lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
    return json.loads(lines[0])

def main():
    #get our data as an array from read_in()    
    path = sys.argv[1]
    
    print(path)

    

#start process
if __name__ == '__main__':
    main()