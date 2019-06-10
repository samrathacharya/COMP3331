import socket

def Main():
    host = '127.0.0.1'
    port = 5004 #NOTE: Different port to server
    
    server = (host,5003)  #Sotre turple of host and port in server
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host,port))
    
    message = raw_input("Enter message: ")
    while message!='q':
        s.sendto(message, server)   #Send message to server
        data, addr = s.recvfrom(1024)
        print "Recevied from server: "+ str(data)
        message = raw_input("Enter message: ")
    s.close()
        
    
if __name__ == '__main__':
    Main()

