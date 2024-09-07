import socket
import threading
import chat_pb2  # Import the generated protobuf classes
from client import FORMAT
import  struct
SERVER = '0.0.0.0'
PORT = 5050
HEADER = 64
DISCONNECT_MSG = 'disconnect!'

class ClientConnection:
    def __init__(self, client_socket, nickname):
        self.client_socket = client_socket
        self.nickname = nickname

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
connected_clients = []

def broadcast(message, sender_client_socket):
    for client in connected_clients:
        if client.client_socket != sender_client_socket:
            try:
                client.client_socket.send(message)
            except Exception as e:
                print(f"[ERROR] Failed to send message to {client.nickname}: {e}")


def client_handler(client_socket, addr):
    try:
        nickname_length = client_socket.recv(HEADER).decode(FORMAT)
        if nickname_length:
            nickname_length = int(nickname_length.strip())
            nickname_data = client_socket.recv(nickname_length)
            nickname_data = bytes(nickname_data)
            client_hello = chat_pb2.ClientHello()
            client_hello.ParseFromString(nickname_data)
            client_name = client_hello.nickname
            new_client = ClientConnection(client_socket, client_name)
            connected_clients.append(new_client)
            print(f'[CONNECTED] {client_name}is connected.')
            connected = True

        while connected:
            try:
               # msg_length = client_socket.recv(HEADER).decode(FORMAT)
               # if msg_length:
                   # msg_length = int(msg_length.strip())
                   # msg_data = client_socket.recv(msg_length)
                   # msg_data = bytes(msg_data)
                   # client_msg = chat_pb2.ClientSendMsg()
                   # client_msg.ParseFromString(msg_data)
                   # msg = client_msg.msg
                   msg_len_bytes = socket.recv(4)
                   msg_len = struct.unpack("<L", msg_len_bytes)[0]
                   msg_data = socket.recv(msg_len)
                   client_msg = chat_pb2.ClientSendMsg()
                   client_msg.ParseFromString(msg_data)

                   if msg_data == DISCONNECT_MSG:
                       connected = False
                   else:
                       print(f"[{client_name}] : {msg_data}")
                       broadcast(msg_data, client_socket)

            except Exception as e:
                print(f"[ERROR] {e}")
                connected = False
    finally:
        connected_clients.remove(new_client)
        client_socket.close()
        print(f'[DISCONNECTED] {client_name} ({addr}) disconnected.')

def bind_server():
    try:
        server.bind(ADDR)
        print(f'[RUN] Running the server {SERVER} {PORT}')
    except socket.error as e:
        print(f'[ERROR] Cannot bind the server: {e}')

def start_listening():
    server.listen()
    print('[LISTENING] Server is listening...')
    while True:
        client_socket, addr = server.accept()
        print(f"[NEW CONNECTION] {addr} connected.")
        thread = threading.Thread(target=client_handler, args=(client_socket, addr))
        thread.start()
        print(f"\n[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

def main():
    bind_server()
    start_listening()

if __name__ == '__main__':
    main()
