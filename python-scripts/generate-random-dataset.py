import sys, json, random, pandas as pd, numpy as np

def main():
    n = sys.argv[1]
    cols = ["A","B"]
    df = pd.DataFrame(columns=cols)
    for i in range(int(n)):
        df.loc[i] = [np.random.randint(1,100),np.random.randint(1,1000)]
    file_name = "data-"+str(int(int(n)/1000))+"k.csv"
    df.to_csv(file_name, index=False)

#start process
if __name__ == '__main__':
    main()