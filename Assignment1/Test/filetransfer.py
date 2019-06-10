import socket
import sys
import threading
import time
import os
import random

ENCODING = 'utf-8'
HEADERSIZE = 25
DROP_PROB = 0.3
host = '127.0.0.1'
initPort = int(sys.argv[1])
peer1 = int(sys.argv[2])
MSS = 300
FILE_MSG = "FILE:"
fsSize = sys.getsizeof(FILE_MSG)
adjustedMSS = 300

class FileSender(threading.Thread):

    def __init__(self, fileName,initPort,peer1):
        threading.Thread.__init__(self, name="file_receiver")
        self.fileName = fileName
        self.port = initPort
        self.toSendPort = peer1
        self.lastACK = 0
        self.sentContent = False
        self.lastSentFrom = 0
        self.lendata = 0
        self.sentTime = time.time()

        #Flag: 0 = snd, 1 = retransmission
    def sender(self,fileName,bytesFrom,toSendPort,flag):
   
        udpSenderSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udpSenderSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpSenderSocket.bind((host,self.port))
        f = open(fileName,'rb')
        randomNum = random.uniform(0,1)
        #change this to 
        if(randomNum > DROP_PROB and self.port != 5556):
            f.seek(bytesFrom)
            self.lastSentFrom = bytesFrom
            bytesToSend = f.read(adjustedMSS)
            lendata = len(bytesToSend)
            self.lendata = lendata
            ackNum = bytesFrom+lendata
            self.senderAck = ackNum
            header = "FILE:"+str(bytesFrom)+":"+str(ackNum)+":"
            header = f'{header:<{HEADERSIZE}}'
            header = bytes(header,ENCODING)
            toSend = header+bytesToSend
            print("**Sending from: "+str(bytesFrom)+"to "+str(ackNum))
            #print(str(toSend))
            udpSenderSocket.sendto(toSend,(host,self.toSendPort))
            f.close()
            self.sentContent = True
            self.sentTime = time.time()
            
            #Write to log
            r = open('responding_log.txt','a')
            bytesFrom+=1
            if flag==0:
                event = '<snd>     '
            elif (flag==1 or randomNum<DropProb):
                event = '<Drop>     '
                rest = '<'+str(time.time())+'>       '+'<'+str(bytesFrom)+'>     '+'<'+str(lendata)+'>     '+'<0>\n'
                r.write(event+rest)
                event = '<RTX>      '
                
            rest = '<'+str(time.time())+'>       '+'<'+str(bytesFrom)+'>     '+'<'+str(lendata)+'>     '+'<0>\n'    
            r.write(event+rest)
            
        udpSenderSocket.close()

            

    def receiver(self,initPort):
  
        udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udpSocket.bind((host,self.port))
        udpSocket.settimeout(1)
        udpNew = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        ackBytes = 0
        seq_num = 0
        fileSize = os.path.getsize(self.fileName)
        #print(fileSize)
        while True:
            if (ackBytes >= fileSize):
                    print("oops")
                    break
            else:
                try:
                    full_message = ""
                    data, addr = udpSocket.recvfrom(1024)
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
                            f = open('old_'+self.fileName, 'ab')
                            f.write(data[25:])
                            
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
                            print("Sending ACK for: " +ack_num)
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
                        print(ackBytes)
                        if(full_message[:3] == "ACK"):
                            self.sentContent = False        #5555 sends content, when it receives ACK, it knows that content is delivered
                            print("Received ACK for: "+str(ackBytes))
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
                    elif (self.sentContent == False and self.port!=5556):
                        print("Content not sent. Send content again from "+str(self.lastACK))
                        self.sender(self.fileName,self.lastACK,self.toSendPort,1)
        udpSocket.close()

                
    def run(self):
        self.sender(self.fileName,0,self.toSendPort,0)
        self.receiver(self.port)
        



def main():
    fileToSend = input("Enter file to send to next peer: ")
    fileSender = FileSender(fileToSend,initPort,peer1)
    treads = [fileSender.start()]


if __name__ == '__main__':
    main()

