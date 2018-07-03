# server.py
import socket,sys
import numpy as np, pandas as pd, pyarrow as pa



def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    try:
        while True:
            # the input is in bytes, so decode it
            input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

            # MAX_BUFFER_SIZE is how big the message can be
            # this is test if it's sufficiently big
            siz = sys.getsizeof(input_from_client_bytes)
            if  siz >= MAX_BUFFER_SIZE:
                print("The length of input is probably too long: {}".format(siz))

            # decode input and strip the end of line
            input_from_client = input_from_client_bytes.decode("utf8").rstrip()
            try:
                if input_from_client == "exit":
                    break
                elif 'read' in input_from_client:
                    data_df_final = readData("arrow",input_from_client.split(":::")[1])
                    res = "data read successfully"
                else:
                    print(globals())
                    print(locals())
                    if 'data_df_final' in locals():
                        res = str(getColumns(data_df_final))
                    else:
                        res = "first read some data :-P"
                print("Result of processing {} is: {}".format(input_from_client, res))
            except:
                res= "some error"
                print("some error occured")
            vysl = res.encode("utf8")  # encode the result string
            conn.sendall(vysl)  # send it to client
    except ConnectionAbortedError:
        conn.close()  # close connection
    print('Connection ' + ip + ':' + port + " ended")

def start_server():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("127.0.0.1", 12345))
        print('Socket bind complete')
    except (ConnectionResetError,socket.error) as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    soc.listen(10)
    print('Socket now listening')

    # for handling task in separate jobs we need threading
    from threading import Thread

    # this will make an infinite loop needed for 
    # not reseting server for every client
    # a = True
    while True:
        try:
            conn, addr = soc.accept()
            ip, port = str(addr[0]), str(addr[1])
            print('Accepting connection from ' + ip + ':' + port)
            try:
                Thread(target=client_thread, args=(conn, ip, port)).start()
            except:
                print("Terible error!")
                import traceback
                traceback.print_exc()
                break
        except KeyboardInterrupt:
            if soc:  # <---
                soc.close()
            break
    soc.close()


def getColumns(data):
    '''
        description:
        Column names in a data frame
        input:
            data: pandas df
        Output:
            list of column names
    '''
    return list(data.columns)
    # sys.stdout.flush()

def readArrowToDF(source):
    '''
        description:
            Read arrow file from disk using apache pyarrow
        input:
            source: file path
        return:
            pandas dataframe
    '''
    source = source+".arrow"
    reader = pa.RecordBatchStreamReader(source)
    pa_df = reader.read_all()
    return pa_df.to_pandas()

def readCSV(source):
    '''
        description:
            Read csv file from disk using pandas
        input:
            source: file path
        return:
            pandas dataframe
    '''
    df = pd.read_csv(source)
    return df

def readData(load_type,file):
    '''
        description:
            Read file as per the load type
        input:
            load_type: csv or arrow
            file: file path
        return:
            pandas dataframe
    '''
    #file is in the uploads/ folder, so append that to the path
    file = str("uploads\\"+file)
    if load_type == 'csv':
        data = readCSV(file)
    elif load_type == 'arrow':
        data = readArrowToDF(file)
    data_df_final = data
    return data

if __name__ == '__main__':
    start_server()
