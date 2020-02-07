import asyncio
import random
import time
from threading import current_thread


class ChatServerAsync:
    def __init__(self, port):
        self.port = port
        self.clients = {}
        self.writers = {}

    async def run_server(self, reader, writer):
        while True:
            msg = (await reader.read(4096)).decode()
            print(f"[{current_thread().getName()}] Server received {msg}")
            await self.handle_client(msg, writer)

    async def handle_client(self, msg, writer):
        try:
            cmd, *params = msg.split(",", 1)
        except Exception as e:
            print(f"Something went wrong handling client: {e}")
            raise

        if cmd == "register":
            [user] = params
            self.clients[user] = writer
            self.writers[writer] = user
            print(f"{user} has joined the chat")
            writer.write("ack".encode())
            await writer.drain()
        elif cmd == "list":
            names = self.clients.keys()
            writer.write((", ".join(names) + "\n").encode())
            await writer.drain()
        elif cmd == "tell":
            recipient, msg = params[0].split(",", 1)
            recp_writer = self.clients.get(recipient)
            if recp_writer is None:
                writer.write(f"Unkown user: {recipient}".encode())
                await writer.drain()
            else:
                recp_writer.write(f"{self.writers[writer]}: {msg}".encode())
                await recp_writer.drain()


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

    async def recv_msg(self, reader):
        while True:
            msg = (await reader.read(4096)).decode()
            print(f"[{current_thread().getName()}] {self.name} received: {msg}\n")

    # Dummy client that just sends a few canned commands
    async def run_client(self):
        reader, writer = await asyncio.open_connection(self.srv_host, self.srv_port)

        writer.write(f"register,{self.name}".encode())
        await writer.drain()
        print(f"{self.name} is registering")
        await reader.read(4096)

        writer.write("list,all".encode())
        await writer.drain()
        users = (await reader.read(4096)).decode().split(", ")

        asyncio.create_task(self.recv_msg(reader))

        while True:
            recp = random.choice(users)
            msg = random.choice(self.THINGS_TO_SAY)
            writer.write(f"tell,{recp},{msg}".encode())
            await writer.drain()
            await asyncio.sleep(random.randint(3, 7))


async def main():
    srv_port = random.randint(10000, 55555)
    srv_host = "127.0.0.1"
    srv = ChatServerAsync(srv_port)

    await asyncio.start_server(srv.run_server, srv_host, srv_port)

    users = [
        "watermelonFIEND",
        "thr34dpooL",
        "st4cktr4c3",
        "Alex",
        "Karl",
        "Spot",
        "Henry",
    ]
    tasks = []
    for username in random.sample(users, 5):
        user = User(username, srv_host, srv_port)
        tasks.append(asyncio.create_task(user.run_client()))

    await asyncio.gather(*tasks)



if __name__ == "__main__":
    asyncio.run(main())
