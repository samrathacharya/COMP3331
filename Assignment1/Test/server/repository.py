class Queue:
    def __init__(self):
        self.queue = []

    def add_message(self, sender, message):
        self.queue.append({"sender": sender, "message": message})

    def messages_waiting(self):
        return len(self.queue) > 0

    def pop_message(self):
        return self.queue.pop()


class Users:
    def __init__(self):
        self.users = []

    def add_user(self, name, host, port):
        self.users.append({"name": name, "host": host, "port": int(port)})

    def all_users(self):
        return self.users

