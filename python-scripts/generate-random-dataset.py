import sys, json, random, pandas as pd, numpy as np

def main():
    n = sys.argv[1]
    cols = ["A","B","C"]
    a = np.random.randint(1,1000,(int(n),3))
    
    # for i in range(int(n)):
    #     # print(".",end="")
    #     a = str(random.randrange(1,100))+","+str(random.randrange(1,1000))
    #     print(a)
    file_name = "data-"+str(int(int(n)/1000))+"k.csv"
    pd.DataFrame(a,columns=cols).to_csv(file_name, index=False)
    # df.to_csv(file_name, index=False)

#start process
if __name__ == '__main__':
    main()