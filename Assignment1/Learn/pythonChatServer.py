import socket
import sys
import threading
from _thread import *

class Server:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []    #Empty list of connections
        
    def __init__(self):
        self.s.bind(('127.0.0.1',5556))
        self.s.listen(1)     #Only listen to one connection
        
    def handler(self,conn,addr):
        while True:
            data = conn.recv(2048) #Receive data from connection
            reply = 'From: '+str(addr)+ data.decode('utf-8')
            for connection in self.connections:
                if connection != conn:
                    connection.send(str.encode(reply))  
            if not data:
                #Disconnect the user
                reply = "User " +str(conn)+":"+str(addr)+" has disconnected"
                self.connections.remove(conn)
                conn.close() 
                for connection in self.connections:
                    connection.send(str.encode(reply))
                break

                
    def run(self):
        while True: 
            conn, addr = self.s.accept()
            print('connected to: '+addr[0]+':'+str(addr[1]))
            cThread = threading.Thread(target=self.handler, args=(conn,addr))
            cThread.daemon = True
            cThread.start()
           # start_new_thread(self.handler,(conn,addr))  
            self.connections.append(conn)
            print(self.connections)
        
        
class Client:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #Pass port in as an argument while initialising the program
    def __init__(self, port):
        self.s.connect(('127.0.0.1',port))
        #Create new thread that sends data
        iThread = threading.Thread(target=self.sendMsg)
        iThread.daemon = True
        iThread.start()
        
        #Loop that continually receives data
        while True:
            data = self.s.recv(1024)
            reply = data.decode('utf-8')
            if not data:
                break
            print(reply)
            
        
    def sendMsg(self):
        while True:
            self.s.send(bytes(input("You: "),'utf-8'))
 
        
   
        
            
#If more than one command line argument, then you want to be the client
if (len(sys.argv) > 1):
    client = Client(int(sys.argv[1]))
else:
    server = Server()
    server.run()
