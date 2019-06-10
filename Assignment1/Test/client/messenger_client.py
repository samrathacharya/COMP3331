import socket
import threading

ENCODING = 'utf-8'


class Receiver(threading.Thread):

    def __init__(self, my_host, my_port):
        threading.Thread.__init__(self, name="messenger_receiver")
        self.host = my_host
        self.port = my_port

    def listen(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((self.host, self.port))
        sock.listen(10)
        while True:
            connection, client_address = sock.accept()
            try:
                full_message = ""
                while True:
                    data = connection.recv(16)
                    full_message = full_message + data.decode(ENCODING)
                    if not data:
                        print(full_message.strip())
                        break
            finally:
                connection.shutdown(2)
                connection.close()

    def run(self):
        self.listen()


class Sender(threading.Thread):

    def __init__(self, server_host, server_port, user_name, local_host, local_port):
        threading.Thread.__init__(self, name="messenger_sender")
        self.host = server_host
        self.port = server_port
        self.user_name = user_name
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.sendall("connect_request|{}|{}|{}".format(user_name, local_host, local_port).encode(ENCODING))
        s.shutdown(2)
        s.close()

    def run(self):
        while True:
            message = input("")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            s.sendall("from:{}|{}".format(self.user_name, message).encode(ENCODING))
            s.shutdown(2)
            s.close()


def main():
    my_host = input("host: ")
    my_port = int(input("port: "))
    receiver = Receiver(my_host, my_port)
    server_host = input("server host: ")
    server_port = int(input("server port: "))
    user_name = input("user name: ")
    sender = Sender(server_host, server_port, user_name, my_host, my_port)
    treads = [receiver.start(), sender.start()]


if __name__ == '__main__':
    main()
