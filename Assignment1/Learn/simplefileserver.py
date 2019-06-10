#Server sends all bytes from ne file over network
#Waits for clients to connect and request a file

import socket
import threading 
import os

host = '127.0.0.1'

def RetrFile(name,toSendPort):
    filename,addr = sock.recvfrom(1024)
    filename = filename.decode('utf-8')
    if (os.path.isfile(filename)):
        toSend = "EXISTS"+str(os.path.getsize(filename))
        sock.sendto(toSend.encode('utf-8'),(host,toSendPort))
        with open(filename, 'rb') as f:
            bytesToSend = f.read(1024)
            sock.sendto(bytesToSend,(host,toSendPort))
            #If file >1024 bytes
            while (bytesToSend != ""):
                #Get more bytes to send
                bytesToSend = f.read(1024)
                sock.sendto(bytesToSend,(host,toSendPort))
    else:  
        toSend = "ERR: File does not exist"
        sock.sendto(toSend.encode('utf-8'),(host,toSendPort))
    sock.close()

def Main():
    port = 5402
    toSendPort = 5401
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host,port))
    print("Server started")
    while True: 
        t = threading.Thread(target=RetrFile, args=("retrThread",toSendPort))
        t.start()
    s.close()

if __name__ == "__main__":
    Main() 
            
