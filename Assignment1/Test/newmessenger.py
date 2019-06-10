import socket
import threading
import time

ENCODING = 'utf-8'


class Receiver(threading.Thread):

    def __init__(self, my_host, my_port):
        threading.Thread.__init__(self, name="messenger_receiver")
        self.host = my_host
        self.port = my_port
        self.receive = False

    def listen(self):
        udpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        udpSocket.bind((self.host,self.port))
        while True:
            self.receive = False
            try:
                full_message = ""
                data, addr = udpSocket.recvfrom(1024)
                full_message = full_message + data.decode(ENCODING)
                if (full_message != ""):
                    print("A ping request message was received")
                ack_msg = "PING RESPONSE"
                ack_msg = ack_msg.encode(ENCODING)
                udpSocket.sendto(ack_msg,addr)
                if not data:
                    print("error not data")
                    break
            finally:
                print("")
          
    def run(self):
        self.listen()


class Sender(threading.Thread):

    def __init__(self, my_friends_host, my_friends_port):
        threading.Thread.__init__(self, name="messenger_sender")
        self.host = my_friends_host
        self.port = my_friends_port

    def run(self):
        while True:
            time.sleep(5)
            message = "PING REQUEST"
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((self.host, self.port))
            s.sendto(message.encode(ENCODING),(self.host,self.port))
            data,addr = s.recvfrom(1024)
            data = data.decode(ENCODING)
            if (data != ""):
                print("A ping response message was received from: ")
            s.shutdown(2)
            s.close()


def main():
    my_host = input("which is my host? ")
    my_port = int(input("which is my port? "))
    receiver = Receiver(my_host, my_port)
    my_friends_host = input("what is your friend's host? ")
    my_friends_port = int(input("what is your friend's port?"))
    sender = Sender(my_friends_host, my_friends_port)
    treads = [receiver.start(), sender.start()]


if __name__ == '__main__':
    main()
