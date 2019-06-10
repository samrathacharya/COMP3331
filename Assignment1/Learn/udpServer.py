import socket
import time
import pickle

"""
HEADERSIZE = 10
d = {1: "Hey", 2: "There"}
msg = pickle.dumps(d)
print(msg)

"""
def Main():
    host = '127.0.0.1'
    port = 5003

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)#Override defaults and change to datagram
    
    s.bind((host,port))
    print "server started"
    
    while True:
        data, addr = s.recvfrom(1024)   #Receive data and address recieved from
        print "Data received from: " +str(addr)
        print "Message: "+str(data)
        data = str(data).upper()
        print "sending data" + str(data)
        s.sendto(data, addr)    #Send back to user
    s.close()

    
if __name__ == '__main__':
    Main()
