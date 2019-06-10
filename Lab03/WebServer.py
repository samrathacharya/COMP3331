#!/usr/bin/env python3.5
import sys
from socket import *

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
#Prepare a server socket
serverSocket.bind(('',serverPort)) #this binds the port
serverSocket.listen(1)
while True:
    #Get connection ready
    #Receiver 1024 bytes of data
    print("Server is ready to receive data")
    connectionSocket, addr = serverSocket.accept()
    
    try:
        message = connectionSocket.recv(1024)
        print(message)
        
        #Get the filename
        fileName = message.split()[1]
        print(filename)
        #Open and output file data
        f = open(filename[1:]) #opens the file
        outputdata = f.read() 
        print (outputdata) 
        
        #Send HTTP line into socket
        #Okay HTTP messsage
        connectionSocket.send('HTTP/1.1 200 OK\n\n')
        #Close the message
        connectionSocket.send('Connection: close\n')
        lenOfString = 'Content-Length: '+ str(len(outputdata))+'\n';
        connectionSocket.send(lenOfString) #length of the message
        connectionSocket.send('Content-Type: text/html\n') #type of message
        connectionSocket.send('\n\n')

        #Send the data and close the socket
        connectionSocket.send(outputdata)
        connectionSocket.close()
    
    #If there is an error...
    except IOError:
        connectionSocket.send('\n')
        Error404 = "404 Not Found: "+ filename + "\n" #message
        connectionSocket.send(Error404)
        connectionSocket.close()
        
    #at the end
    pass
    serverSocket.close() #close server socket
    


    
