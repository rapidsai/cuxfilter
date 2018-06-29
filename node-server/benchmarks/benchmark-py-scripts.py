'''
    Automate benchmarking script.py individually

    Output: text file that can be directly dumped into a google sheet
'''
import sys,timeit as t,os
sys.path.insert(0, '../../python-scripts')
from script import *

files = ['data-1000k','data-10000k','data-100000k']
pandas_with_csv = {}
pandas_with_arrow = {}
numba_with_csv = {}
numba_with_arrow = {}

# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')

# Restore
def enablePrint():
    sys.stdout = sys.__stdout__


def initiate(file):
    pandas_with_csv[file] = []
    pandas_with_arrow[file] = []
    numba_with_csv[file] = []
    numba_with_arrow[file] = []


def exec(file, type, processing, load_type, columnName='A'):
    data = readData(load_type,file)
    if type == 'hist':
        getHist(processing,data,columnName)
    elif type == 'columns':
        getColumns(data)


def getHist(file,name, numIter=2):
    pandas_csv = t.timeit("exec(file,'hist','pandas','csv')",setup="file="+file,number=numIter)
    pandas_with_csv[name].append(pandas_csv.best)
    pandas_arrow = t.timeit("exec(file,'hist','pandas','arrow')",number=numIter)
    pandas_with_arrow[name].append(pandas_arrow.best)
    numba_csv = t.timeit("exec(file,'hist','numba','csv')",number=numIter)
    numba_with_csv[name].append(numba_csv.best)
    numba_arrow = t.timeit("exec(file,'hist','numba','arrow')",number=numIter)
    numba_with_arrow[name].append(numba_arrow.best)

def getCols(file,name,numIter=2):
    pandas_csv = t.timeit("exec(file,'columns','numpy','csv')",setup="file='"+file+"'",number=numIter)
    pandas_with_csv[name].append(pandas_csv.best)
    pandas_arrow = t.timeit("exec(file,'hist','pandas','arrow')",number=numIter)
    pandas_with_arrow[name].append(pandas_arrow.best)
    numba_csv = t.timeit("exec(file,'columns','numba','csv')",number=numIter)
    numba_with_csv[name].append(numba_csv.best)
    numba_arrow = t.timeit("exec(file,'columns','numba','arrow')",number=numIter)
    numba_with_arrow[name].append(numba_arrow.best)

def main():
    if len(sys.argv)>1:
        numIter = sys.argv[1]
    else:
        numIter = 2
    for file in files:
        print(file)
        name = file
        os.chdir('../')
        initiate(name)
        getCols(file,name,numIter)
        getHist(file,name,numIter)

#start process
if __name__ == '__main__':
    main()