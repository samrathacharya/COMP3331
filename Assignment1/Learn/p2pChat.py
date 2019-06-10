import socket
import sys
import threading
from _thread import *
import time
from random import randint

class Server:
    connections = []    #Empty list of connections
    peers = []  #List of people connected alongside the server with us
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.bind(('127.0.0.1',5555))
        s.listen(1)     #Only listen to one connection
        print("Server running...")
        while True: 
            conn, addr = s.accept()
            print('connected to: '+addr[0]+':'+str(addr[1]))
            cThread = threading.Thread(target=self.handler, args=(conn,addr))
            cThread.daemon = True
            cThread.start()
            # start_new_thread(self.handler,(conn,addr))  
            self.connections.append(conn)
            self.peers.append(addr[1]) #Append address of peer - port
            print(self.connections)
            self.sendPeers()
        
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
                self.peers.remove(addr[1])
                conn.close() 
                self.sendPeers()    #Update peer list 
                for connection in self.connections:
                    connection.send(str.encode(reply))
                break

    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + str(peer) + ","
        #send new list to all peers
        for connection in self.connections:
            connection.send(b'\x11'+bytes(p,'utf-8'))

       
        
        
class Client:
    def __init__(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #Pass port in as an argument while initialising the program
        s.connect(('127.0.0.1',port))
        #Create new thread that sends data
        iThread = threading.Thread(target=self.sendMsg,args=(s,))
        iThread.daemon = True
        iThread.start()
        
        #Loop that continually receives data
        while True:
            data = s.recv(1024)
            if not data:
                break
            if data[0:1] == b'\x11':
                print("GOt peers")
            else:
                reply = data.decode('utf-8')
                print(reply)
            
        
    def sendMsg(self,s):
        while True:
            s.send(bytes(input("You: "),'utf-8'))
 
        
   
        
            
#If more than one command line argument, then you want to be the client
if (len(sys.argv) > 1):
    client = Client(int(sys.argv[1]))
else:
    server = Server()
   # while True:
    #    print("Trying to connect")
        #Wait random time until client  becomes the new server
     #   time.sleep(randint(1,5))
