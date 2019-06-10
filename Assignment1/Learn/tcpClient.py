import socket

def Main():
    host = '127.0.0.1'
    port = 5003
    
    s = socket.socket()
    s.connect((host,port))  #Form connection
    
    message = raw_input("Enter thing: ")
    while message != 'q':   #While not terminated
        s.send(message)     #Send message
        data = s.recv(1024)  #Receive data
        print "From server: "+str(data)
        message = raw_input("Enter thing: ")
    s.close()

if __name__ == '__main__':
    Main()
