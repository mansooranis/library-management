import socket
import os
from _thread import *
import datetime

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waitiing for a Connection..')
ServerSocket.listen(5)

def threaded_client(connection):
    while True:
        F = open("liblogs", "a")
        data = connection.recv(2048)
        msg = data.decode('utf-8')
        e = datetime.datetime.now()
        F.write(f"{msg} at {e.hour}:{e.minute}:{e.second} \n")
        print ("%s at %s:%s:%s" % (msg,e.hour, e.minute, e.second))
        if not data:
            break
    connection.close()
while True:
    Client, address = ServerSocket.accept()
    start_new_thread(threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))


ServerSocket.close()