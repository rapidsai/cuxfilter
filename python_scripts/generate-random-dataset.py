import sys, json, random, pandas as pd, numpy as np

def main():
    n = sys.argv[1]
    m = sys.argv[2]
    cols = []
    
    for i in range(m):
        cols.append("col-"+i)

    a = np.random.rand(1,1000,(int(n),int(m)))
    file_name = "../data/data-"+str(int(int(n)/1000))+"k.csv"
    pd.DataFrame(a,columns=cols).to_csv(file_name, index=False)
    print("file saved to ",file_name)

#start process
if __name__ == '__main__':
    main()