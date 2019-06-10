#!usr/bin/python3
import socket
import sys
import threading

host = '127.0.0.1'
initPort = sys.argv[1]
peer1 = sys.argv[2]
peer2 = sys.argv[3]
MSS = sys.argv[4]
dropProb = sys.argv[5]

###TEST###
print("Port: "+initPort)
print ("Successor 1: "+peer1)
print ("Successor 2: "+peer2)
print ("MSS: "+MSS)
print ("Drop Prob: "+dropProb)


class Node:
    #Intialise udpSocket
    udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    #Initialise TCP Socket
    tcpSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    #tcpSocket.connect()

    def __init__(self,port):
        port = int(port)
        self.udpSocket.bind((host,port))
        self.tcpSocket.bind((host,port))

    def run(self):
        while True:
            #Create thread for UDP socket to send messages
            udpSendThread = threading.Thread(target=self.udpSendMsg)
            udpSendThread.daemon = True
            udpSendThread.start()
            #Create thread for UDP socket to receive messages
            udpRcvThread = threading.Thread(target=self.udpReceiveMsg)
            udpRcvThread.daemon = True
            udpRcvThread.start()

    def udpSendMsg(self):
        while True:
            toSend = input("")
            print("Sending message to successor 1:"+peer1)
            data = "DATA: Sending message to successor 1"+toSend
            self.udpSocket.sendto(data,peer1)
        self.udpSocket.close()

    def udpReceiveMsg(self):
        while True:
            data,addr = self.udpSocket.recvfrom(1024)
            print("Messaged received from: "+str(addr[0])+"Content: "+str(data))
        self.udpSocket.close()

node = Node(int(initPort))
node.run()

       





