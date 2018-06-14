import sys, json, random

def main():
    n = sys.argv[1]
    print("A,B")
    for i in range(int(n)):
        print(str(random.randrange(1,100))+","+str(random.randrange(1,10000)))


#start process
if __name__ == '__main__':
    main()