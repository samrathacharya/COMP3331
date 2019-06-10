#Client will ask user for filename 
#Download file and add new_ as prefix

import socket
import sys

def Main():
    host = '127.0.0.1'
    port = 5401

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host,port))
    filename = input("Filename: ")
    if filename != "":
        s.send(filename.encode('utf-8'))
        data = s.recv(1024)
        data = data.decode('utf-8')
        if data[:6] == "EXISTS":
            filesize = int(data[6:])
            f = open('new_'+filename, 'wb')
            data = s.recv(1024)
            totalRecv = len(data)
            f.write(data)
            while (totalRecv<filesize):
                data = s.recv(1024)
                totalRecv+= len(data)
                f.write(data)
            print("Downlaod complete")
        else:
            print("File does not exist")
    s.close()

if __name__ == "__main__":
    Main()
