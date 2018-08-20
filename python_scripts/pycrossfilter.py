# server.py
import socket
import sys
import time
from pycrossfilter_utils import process_input_from_client


def client_thread(conn, ip, port, MAX_BUFFER_SIZE = 4096):

    try:
        while True:
            # the input is in bytes, so decode it
            input_from_client_bytes = conn.recv(MAX_BUFFER_SIZE)

            # MAX_BUFFER_SIZE is how big the message can be. This tests if it's sufficiently big
            siz = sys.getsizeof(input_from_client_bytes)
            if  siz >= MAX_BUFFER_SIZE:
                print("The length of input is probably too long: {}".format(siz))

            # decode input and strip the end of line
            start_time = time.perf_counter()
            input_from_client_all = input_from_client_bytes.decode("utf8").rstrip().split("///")

            for input_from_client in input_from_client_all:
                if(len(input_from_client)>0):
                    #response for the request as per input_from_client
                    res = process_input_from_client(input_from_client)
                    res = append_time_to_response(res,start_time)
                    # send it to client
                    conn.sendall(res)

    except ConnectionAbortedError:
        conn.close()  # close connection
    print('Connection ' + ip + ':' + port + " ended")


def append_time_to_response(res,start_time):
    elapsed = time.perf_counter() - start_time
    #appending
    if len(res.split(":::"))>2:
        res = res+","+str(elapsed)+"////"
    else:
        res = res+":::"+str(elapsed)+"////"
    # encode the result string
    res = res.encode("utf8")
    return res


def start_server():
    num_connections = int(sys.argv[1])
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # this is for easy starting/killing the app
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Socket created')

    try:
        soc.bind(("0.0.0.0", 3001))
        print('Socket bind complete')
    except (ConnectionResetError,socket.error) as msg:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    #Start listening on socket
    soc.listen(10)
    print('Socket now listening')

    # for handling task in separate jobs we need threading
    from threading import Thread

    # this will make an infinite loop needed for not reseting server for every client
    threads = []
    for _ in range(num_connections):
        try:
            conn, addr = soc.accept()
            ip, port = str(addr[0]), str(addr[1])
            print('Accepting connection from ' + ip + ':' + port)
            try:
                threads.append(Thread(target=client_thread, args=(conn, ip, port)))
                threads[-1].start()
            except:
                print("Terible error!")
                import traceback
                traceback.print_exc()
                # break
        except KeyboardInterrupt:
            if soc:  # <---
                soc.close()
            # break
        for t in threads:
            print("thread is alive?: ",t.is_alive())
    soc.close()



if __name__ == '__main__':
    start_server()
