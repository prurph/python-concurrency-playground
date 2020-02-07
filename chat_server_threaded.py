import random
import socket
import sys
import time
from threading import Lock, Thread


class ChatServerThreaded:
    def __init__(self, port):
        self.port = port
        self.lock = Lock()
        self.clients = {}

    def run_server(self):
        sock = socket.socket()
        sock.bind(("", self.port))
        sock.listen(5)

        while True:
            client_sock, addr = sock.accept()
            Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()

    def handle_client(self, client_sock):
        user = "unknown"

        while True:
            try:
                cmd, *params = client_sock.recv(4096).decode().split(",", 1)
            except Exception as e:
                print(f"Something went wrong handling client: {e}")
                raise

            if cmd == "register":
                [user] = params
                with self.lock:
                    self.clients[user] = client_sock
                print(f"{user} has joined the chat")
                client_sock.send("ack".encode())
            elif cmd == "list":
                with self.lock:
                    names = self.clients.keys()
                client_sock.send((", ".join(names) + "\n").encode())
            elif cmd == "tell":
                recipient, msg = params[0].split(",", 1)
                with self.lock:
                    recp_sock = self.clients.get(recipient)
                if recp_sock is None:
                    client_sock.send(f"Unkown user: {recipient}".encode())
                else:
                    recp_sock.send(f"{user}: {msg}".encode())


class User:
    THINGS_TO_SAY = [
        "Hey",
        "I just met you",
        "This is crazy",
        "Here's my number",
        "Call me, maybe?",
    ]

    def __init__(self, name, srv_host, srv_port):
        self.name = name
        self.srv_host = srv_host
        self.srv_port = srv_port

    def recv_msg(self, srv_sock):
        while True:
            print(f"{self.name} received: {srv_sock.recv(4096).decode()}")

    # Dummy client that just sends a few canned commands
    def run_client(self):
        srv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv_sock.connect((self.srv_host, self.srv_port))

        srv_sock.send(f"register,{self.name}".encode())
        print(f"{self.name} is registering")
        srv_sock.recv(4096).decode()

        time.sleep(3)

        srv_sock.send("list,all".encode())
        users = srv_sock.recv(4096).decode().split(", ")

        Thread(target=self.recv_msg, args=(srv_sock,), daemon=True).start()

        while True:
            recp = random.choice(users)
            msg = random.choice(self.THINGS_TO_SAY)
            srv_sock.send(f"tell,{recp},{msg}".encode())
            time.sleep(random.randint(3, 7))


def main(run_for_s):
    srv_port = random.randint(10000, 55555)
    srv_host = "127.0.0.1"
    srv = ChatServerThreaded(srv_port)

    Thread(target=srv.run_server, daemon=True).start()
    time.sleep(1)

    users = [
        "watermelonFIEND",
        "thr34dpooL",
        "st4cktr4c3",
        "Alex",
        "Karl",
        "Spot",
        "Henry",
    ]
    for username in random.sample(users, 5):
        user = User(username, srv_host, srv_port)
        Thread(target=user.run_client, daemon=True).start()

    time.sleep(run_for_s)


if __name__ == "__main__":
    main(int(sys.argv[1]))
