import socket #import socket module

def Main():
    #set host and port
    host = '127.0.0.1'
    port = 5003
    
    s = socket.socket() #Make new socket object
    s.bind((host,port))#Bind to host and port
    
    s.listen(1) #Listen to one connection at a time
    c,addr = s.accept()     #accept() returns the connection and address
    print "Connection formed: "+str(addr)
    
    #While talking to the client
    while True:
        data = c.recv(1024) #Receive a max. buffer of 1024 bytes from client
        if not data:
            break;  #If connection is broken, exit loop
        print "From user " +str(data)
        data = str(data).upper()    #Make data upper case
        print "Sending "+str(data)
        c.send(data)                #Send data
    c.close()
    
if __name__ == '__main__':
    Main()
