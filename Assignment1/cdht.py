#!usr/bin/python3
import socket
import sys
import threading
import time
import traceback
import os
import random

ENCODING = 'utf-8'
host = '127.0.0.1'
DEF_START = 49999
initPort = DEF_START+int(sys.argv[1])
global peer1
global peer2
seqNum = 0
peer1 = int(sys.argv[2])
peer2 = int(sys.argv[3])
MSS = int(sys.argv[4])
DROP_PROB = float(sys.argv[5])
HEADERSIZE = 25

initPort = initPort
peer1 = DEF_START+peer1
peer2 = DEF_START+peer2
predecessors = []

"""
print("Port: "+str(initPort))
print ("Successor 1: "+str(peer1))
print ("Successor 2: "+str(peer2))
print ("MSS: "+str(MSS))
print ("Drop Prob: "+str(DROP_PROB))"""

class Receiver(threading.Thread):
    def __init__(self, my_host, my_port):
        threading.Thread.__init__(self, name="messenger_receiver")
        self.host = my_host
        self.port = my_port
        self._stopevent = threading.Event()
        self.receivedSeqNums  = [0,0]
        self.expSeqNum = 0
        
    def listen(self):
        udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpSocket.bind(('',self.port))
        global dead
        global peer1
        global peer2
        while (not dead):
            try:
                full_message = ""
                data, addr = udpSocket.recvfrom(1024)
                full_message = full_message + data.decode(ENCODING)
                message=full_message.split(':')
                mType = message[0]
                if (mType == "REQUEST"):
                    receivedFrom = message[1]
                    self.expSeqNum = int(message[2])
                    tag = int(message[3])
                    toPrint = int(receivedFrom)-DEF_START
                    print("A ping request message was received from Peer " +str(toPrint))
                    #Add to predecessors if not already
                    if int(receivedFrom) not in predecessors:
                        if(tag==1):
                            predecessors.insert(0,int(receivedFrom))
                        else:
                            predecessors.insert(1,int(receivedFrom))
                        #sortPredecessors(predecessors)
                        #print("***Added "+receivedFrom+" to predecessors***")
                    #Send response
                    ack_msg = "RESPONSE:"+str(self.expSeqNum)
                    ack_msg = ack_msg.encode(ENCODING)
                    udpSocket.sendto(ack_msg,(self.host,int(receivedFrom)))
                elif (mType == "RESPONSE"):
                    receivedSeqNum = message[1]
                    toPrint = int(addr[1])-DEF_START
                    print("A ping response message was received from Peer " +str(toPrint))
                    if(addr[1] == peer1):
                        self.receivedSeqNums[0] = int(receivedSeqNum)
                    else:
                        self.receivedSeqNums[1] = int(receivedSeqNum)
                    #Peer 1 leaves
                    if(self.expSeqNum-self.receivedSeqNums[0] == 2):
                        toPrint = peer1-DEF_START
                        print("Peer "+str(toPrint)+" is no longer alive")
                        deadPeer = peer1
                        peer1 = peer2
                        toPrint = peer1-DEF_START
                        print("My first successor is now peer "+str(toPrint))
                        #Send message to new peer1 and ask for it's first successor
                        updateSuccessor(peer1,deadPeer)
                        removePredecessor(predecessors,deadPeer)
                    #Peer 2 leaves
                    elif (self.expSeqNum-self.receivedSeqNums[1] == 2):
                        toPrint = peer2-DEF_START
                        print("Peer "+str(toPrint)+" is no longer alive")
                        toPrint = peer1-DEF_START
                        print("My first successor is now peer "+str(toPrint))
                        #Send message to peer 1 and ask for it's first successor
                        updateSuccessor(peer1,peer2)
                        removePredecessor(predecessors,peer2)
                if not data:
                    print("error not data")
                    break
            finally:
                print("")
        
    def run(self):
        self.listen()
        
def sortPredecessors(predecessors):
    if(len(predecessors) != 0):
        predecessors.sort()
        print(predecessors)

def removePredecessor(predecessors,deadPeer):
    if(deadPeer in predecessors):
        predecessors.remove(deadPeer)
        #sortPredecessors(predecessors)
        #print("Removed "+deadPeer+" from predecessors")

def updateSuccessor(peerToAsk,deadPeer):
    #Ask peer for successor over TCP connectiom
    msg = "TELL:"+str(initPort)+":"+str(deadPeer)+":x"
    tcpSender(initPort,peerToAsk,msg)

#GO HERE: Send ping REQUEST and RESPOND messages using UDP
class Sender(threading.Thread):
    def __init__(self, host, myPort, flag):
        threading.Thread.__init__(self, name="messenger_sender")
        self.host = host
        self.initPort = myPort
        self.flag = flag
        self.seqNum = 0

    def run(self):
        global dead
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while not dead:
            global peer1
            global peer2
            time.sleep(20)
            if (self.flag == 'peer1'):
                toSend = peer1
                tag = 1
            else:
                toSend = peer2
                tag = 2
            message = "REQUEST:"+str(self.initPort)+":"+str(self.seqNum)+":"+str(tag)
            #print("SENDING: "+message+"to "+str(toSend))
            s.sendto(message.encode(ENCODING),(self.host,toSend))
            self.seqNum+=1
        s.close()

#TODO: Do we need to check for valid filenames?
def TCPFileRequester(filename,initPort):
    if(os.path.isfile(filename+".pdf")):
        hashed = hash_function(int(filename))
        #print("Hash is: "+str(hashed))
        find_peer(filename, hashed, initPort, peer1,initPort)
    else:
        print("No file")

def hash_function(filename):
    return(filename%256)

def find_peer(filename, hashed,initPort,nextPeer,ogRequestor):
    testinitPort = initPort-DEF_START
    testnextPeer = nextPeer-DEF_START
    testogRequestor = ogRequestor-DEF_START
    prevPeer = predecessors[0]-DEF_START
    """print("Init port: "+str(testinitPort))
    print("next peer: "+str(testnextPeer))
    print("Original Req: "+str(testogRequestor))
    print("Prev peer: "+str(prevPeer))"""
    
    if(prevPeer<hashed and testinitPort>=hashed):
        #FOUND
        toPrint = ogRequestor-DEF_START
        print("File "+filename+" is here. A response message, destined for, Peer "+str(toPrint)+", has been sent")
        print("We now start sending the file...")
        message="F_FOUND:"+str(initPort)+":FOUND:"+filename
        tcpSender(initPort,ogRequestor,message)
        fileSender = FileSender(filename+".pdf",initPort,int(ogRequestor),'S')
        fileSender.start()
        return True
    else:
        if(testnextPeer<testinitPort and hashed>testinitPort):
            #KEEP
            message = "F_REQUEST:"+str(ogRequestor)+":KEEP:"+filename
            tcpSender(initPort,nextPeer,message)
        else:
            #CHECK
            print("File "+filename+" is not stored here")
            print("File request message has been forwarded to my successor.")
            message = "F_REQUEST:"+str(ogRequestor)+":CHECK:"+filename 
            tcpSender(initPort,nextPeer,message)    
           
def tcpSender(initPort,toSend,message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #TODO: Is this port host port or client port?
    s.connect((host,toSend))
    #print("Sending message: "+message)
    message = message.encode(ENCODING)
    s.send(message)
    s.close()

class tcpListener(threading.Thread):
    def __init__(self, host, initPort,peer1):
        threading.Thread.__init__(self, name="tcpListener")
        self.host = host
        self.initPort = initPort
        self.peer1 = peer1

    def run(self):
        global peer1
        #GO HERE: Use TCP to send file request messages
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host,initPort))
        s.listen(3)
        global dead
        global peer2
        global peer1
        while not dead: 
            conn, addr = s.accept()  
            while True:      
                data = conn.recv(1024)
                message = data.decode(ENCODING)
                #print("***TCP MESSAGE: "+message)
                message = message.split(":")
                m_type = message[0]
                m_from = int(message[1])
                m_code = message[2]
                m_file = message[3]
                #If file request message is received 
                if(m_type=='F_REQUEST'):
                    if(m_code == 'KEEP'):   #File is here
                        #Print peer with file found message
                        toPrint = m_from-DEF_START
                        print("File "+m_file+" is here. A response message, destined for "+str(toPrint)+", has been sent")
                        print("We now start sending the file ..")
                        message="F_FOUND:"+str(initPort)+":FOUND:"+m_file
                        tcpSender(initPort,m_from,message) 
                        #Call udpSender 
                        fileSender = FileSender(m_file+".pdf",initPort,m_from,'S')
                        fileSender.start()
                        #print file transfer done message
                        break
                    elif (m_code == 'CHECK'):
                        hashed_name = hash_function(int(m_file))
                        if(find_peer(m_file,hashed_name,self.initPort,peer1,m_from) == True):
                            break
                    #File found by peer
                    else:
                        print("Wrong code")
                    break
                elif(m_type =='F_FOUND'): #Someone found the file
                    toPrint = m_from-DEF_START
                    print("Received a response message from "+str(toPrint)+", which has the file"+m_file)
                    print("We now start receiving the file...")
                    #Open udpReceiver
                    fileSender = FileSender(m_file+".pdf",initPort,m_from,'R')
                    fileSender.start()
                    #Receive file
                    break
                elif(m_type == 'LEAVE'):
                    fSucc = int(m_code)
                    sSucc = int(m_file)
                    toPrint = m_from-DEF_START
                    print("Peer "+str(toPrint)+" will depart from the network")
                    if peer1 == m_from:
                        peer1 = fSucc
                        peer2 = sSucc
                    else:
                        peer2 = sSucc
                    toPrint = peer1-DEF_START
                    print("My first successor is now peer "+str(toPrint))
                    toPrint = peer2-DEF_START
                    print("My second successor is now peer "+str(toPrint)) 
                    break
                elif(m_type == "TELL"):
                    removePredecessor(predecessors,int(m_code))
                    msg = "TOLD:"+str(initPort)+":"+str(peer1)+":"+str(peer2)
                    tcpSender(initPort,m_from,msg)
                    break
                elif(m_type == "TOLD"):
                    peer2 = int(message[2])
                    toPrint = peer2-DEF_START
                    print("My second successor is now peer "+str(toPrint))
                    break
                else:
                    print("error")
        s.close()

class FileSender(threading.Thread):

    def __init__(self, fileName,initPort,toPort,flag):
        threading.Thread.__init__(self, name="file_receiver")
        self.fileName = fileName
        self.port = initPort
        self.toSendPort = toPort
        self.flag = flag
        self.lastACK = 0
        self.sentContent = False
        self.lastSentFrom = 0
        self.lendata = 0
        self.sentTime = time.time()

    #Format: 'FILE:SEQ_NUM:ACK_NO:DATA"
    def sender(self,fileName,bytesFrom,toSendPort,senderFlag):
        #Initialise socket
        udpSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSenderSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpSenderSocket.bind((host,self.port))
        #Initialise file and random num
        f = open(fileName,'rb')
        randomNum = random.uniform(0,1)
        #Send data
        if(randomNum > DROP_PROB and self.flag == 'S'):
            f.seek(bytesFrom)
            self.lastSentFrom = bytesFrom
            bytesToSend = f.read(MSS)
            lendata = len(bytesToSend)
            self.lendata = lendata
            ackNum = bytesFrom+lendata
            self.senderAck = ackNum
            header = "FILE:"+str(bytesFrom)+":"+str(ackNum)+":"
            header = f'{header:<{HEADERSIZE}}'
            header = bytes(header,ENCODING)
            toSend = header+bytesToSend
            #print("**Sending from: "+str(bytesFrom)+"to "+str(ackNum))
            udpSenderSocket.sendto(toSend,(host,self.toSendPort))
            f.close()
            self.sentContent = True
            self.sentTime = time.time()

            #Write log
            r = open('responding_log.txt','a')
            bytesFrom+=1
            if senderFlag==0:
                event = '<snd>     '
            elif (senderFlag==1 or randomNum<DROP_PROB):
                event = '<Drop>     '
                rest = '<'+str(time.time())+'>       '+'<'+str(bytesFrom)+'>     '+'<'+str(lendata)+'>     '+'<0>\n'
                r.write(event+rest)
                event = '<RTX>      '
                
            rest = '<'+str(time.time())+'>       '+'<'+str(bytesFrom)+'>     '+'<'+str(lendata)+'>     '+'<0>\n'    
            r.write(event+rest)

        udpSenderSocket.close()

            
    def receiver(self,initPort):
        #Initialise port
        udpFileSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udpFileSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpFileSocket.bind((host,self.port))
        udpFileSocket.settimeout(1)
        udpNew = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        ackBytes = 0
        seq_num = 0
        fileSize = os.path.getsize(self.fileName)
        #print(fileSize)
        while True:
            if (ackBytes >= fileSize):
                    if(self.flag == 'S'):
                        print("The file has been sent")
                        break
                    elif (self.flag == 'R'):
                        print("The file has been received")
                        break
                    else:
                        break
                    break     
            else:
                try:
                    full_message = ""
                    data, addr = udpFileSocket.recvfrom(1024)
                    header = data[:25].decode(ENCODING).strip().split(':') 
                    lendata = len(data)
                    content = header[0]
                    #print(content)
                    if (content == "FILE"):
                        #Account for duplicate writes
                        self.sentContent = False
                        g = open('requesting_log.txt','a')
                       #print("Received at "+str(time.time()))
                        seq_num = header[1]
                        ack_num = header[2]
                        if(self.lastACK != ack_num):
                            #Write data to file
                            new = open('received_file.pdf', 'ab')
                            new.write(data[25:])
                            
                            #Log files
                            g = open('requesting_log.txt','a')
                            #Write recv
                            event = '<rcv>     '
                            seq_num = int(seq_num)
                            lendata = int(lendata)-25
                            ack_num = int(ack_num)
                            rest = '<'+str(time.time())+'>     '+'<'+str(seq_num)+'>     '+'<'+str(lendata)+'>     '+'<0>\n'
                            g.write(event+rest)
                            
                            #Write send
                            event = '<snd>     '
                            rest = '<'+str(time.time())+'>     '+'<0>     '+'<'+str(lendata)+'>     '+'<'+str(ack_num)+'>\n'
                            g.write(event+rest)
                            ack_num = str(ack_num)
                            #print("Sending ACK for: " +ack_num)
                        else:
                            print("Duplicate content sent - Right after a server timeout")
                        #Send ack
                        #self.sentACK = True
                        self.sentTime = time.time()
                        ack_msg = "ACK:"+ack_num
                        ack_msg = ack_msg.encode(ENCODING)
                        udpNew.sendto(ack_msg,(host,addr[1]))
                    else:
                        full_message = full_message + data.decode(ENCODING)
                        mess = full_message.split(':')
                        ackBytes = int(mess[1])
                        #print(ackBytes)
                        if(full_message[:3] == "ACK"):
                            self.sentContent = False        #5555 sends content, when it receives ACK, it knows that content is delivered
                            #print("Received ACK for: "+str(ackBytes))
                            #Write ACK to file
                            self.lastACK = ackBytes
                            r = open('responding_log.txt','a')
                            event = '<rcv>      '
                            rest = '<'+str(time.time())+'>      '+'<0>     '+'<'+str(self.lendata)+'>      '+'<'+str(self.lastACK)+'>\n'
                            r.write(event+rest)
                            self.sender(self.fileName,ackBytes,addr[1],0)
                          
                            
                except socket.timeout:
                    if(self.sentContent == True):
                            print("ACK not received Send content again from "+str(self.lastSentFrom))
                            self.sender(self.fileName,self.lastSentFrom,self.toSendPort,1)
                    elif (self.sentContent == False and self.flag == 'S'):
                        #print("Content not sent. Send content again from "+str(self.lastACK))
                        self.sender(self.fileName,self.lastACK,self.toSendPort,1)
        #udpSocket.close()

                
    def run(self):
        if(self.flag == 'S'):
            self.sender(self.fileName,0,self.toSendPort,0)
            self.receiver(self.port)
        else:
            self.receiver(self.port)

def leave(host,initPort):
    #Inform predecessors that you are leaving
    msg = "LEAVE:"+str(initPort)+":"+str(peer1)+":"+str(peer2)
    tcpSender(initPort,predecessors[0],msg)
    tcpSender(initPort,predecessors[1],msg)
    return True

def main():
    #Initialise global variables
    global dead
    global peer1
    global peer2
    dead = False
    #Initialise threads
    udpSender = Sender(host,initPort,'peer1')
    udpSender.daemon = True
    udpSenderTwo = Sender(host,initPort,'peer2')
    udpSenderTwo.daemon = True
    udpReceiver = Receiver(host, initPort)
    udpReceiver.daemon = True
    #Start tcp listener
    t_listener = tcpListener(host,initPort,peer1)
    treads = [t_listener.start(),udpSender.start(), udpSenderTwo.start(), udpReceiver.start()]
    userInput = input("Enter command: ")
    while True:
        if (userInput[:8] == 'request '):
            try:
                filename = userInput[8:]
                TCPFileRequester(filename,initPort)
            except:
                print("Please enter a valid file name")
                traceback.print_exc()
        elif (userInput[:4] == 'quit'):
        #GO HERE - TCP for departure
            leave(host,initPort)  
            dead = True
        else:
            print("Please enter valid command")
        userInput = input("Enter command: ")

     


if __name__ == '__main__':
    main()




    


