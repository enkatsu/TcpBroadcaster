import os
import socket
import threading
from dotenv import load_dotenv

load_dotenv()
clients = []
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 32000))
CONNECTION_NUM = int(os.getenv('CONNECTION_NUM', 5))
RECV_BUFFER = int(os.getenv('RECV_BUFFER', 4096))
ECHO = bool(os.getenv('ECHO', False))


class Client:
    def __init__(self, connection: socket.socket, address: str, port: int):
        self.connection: socket.socket = connection
        self.address: str = address
        self.port: int = port

    def equals(self, another):
        return self.address == another.address and self.port == another.port

    def __str__(self):
        return f'<Client address={self.address} port={self.port}>'


def disconnect(client):
    client.connection.close()
    client.connection = None
    clients.remove(client)


def print_connected_clients():
    print('[ ', end='')
    for client in clients:
        print(client, end='')
    print(' ]')


def loop_handler(this_client: Client):
    print(f'connect {this_client}')
    connected = True
    while connected:
        try:
            res = this_client.connection.recv(RECV_BUFFER)

            if len(res) == 0:
                print(f'disconnect {this_client}')
                disconnect(this_client)
                connected = False
                print_connected_clients()
                pass

            for client in clients:
                if this_client.equals(client):
                    print(f'{client} {res}')
                    if ECHO:
                        client.connection.send(res)
                else:
                    client.connection.send(res)

        except socket.timeout:
            print('socket.timeout')
            disconnect(this_client)
            connected = False
        except socket.error:
            print('socket.error')
            disconnect(this_client)
            connected = False
        except Exception as e:
            print(e)
            disconnect(this_client)
            connected = False


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(CONNECTION_NUM)
    print(f'start {HOST}:{PORT}')

    while True:
        try:
            connection, (address, port) = sock.accept()
        except KeyboardInterrupt:
            sock.close()
            exit()
            return
        client = Client(connection, address, port)
        clients.append(client)
        thread = threading.Thread(
            target=loop_handler,
            args=[client],
            daemon=True
        )
        thread.start()


if __name__ == '__main__':
    main()
