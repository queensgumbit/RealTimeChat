import socket
import struct
import threading

import chat_pb2  # Import the generated protobuf classes

SERVER = '0.0.0.0'
PORT = 5050
HEADER = 64
DISCONNECT_MSG = 'disconnect!'

class ClientConnection:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.registered = False
        self.nickname = ""
        self.color = ""
    def set_nickname_and_color(self, nickname,color):
        self.registered = True
        self.nickname = nickname
        self.color = color


    def recv_msg(self):
        msg_len_bytes = self.client_socket.recv(4)
        msg_len = struct.unpack("<L", msg_len_bytes)[0]
        msg_data = self.client_socket.recv(msg_len)
        client_msg = chat_pb2.ChatProtocol()
        client_msg.ParseFromString(msg_data)
        return client_msg



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
connected_clients = []


def broadcast(client_name, message, sender_client_socket):
    # Find the client who sent the message
    sender_client = next((client for client in connected_clients if client.nickname == client_name), None) #The next() function retrieves the first item from an iterator or generator - it no match found it returns none

    if sender_client:
        # Broadcast the message with the sender's color
        incoming_msg = chat_pb2.ChatProtocol(
            incoming=chat_pb2.ClientRecvMsg(
                msg=message.msg,
                sender=client_name,
                color=sender_client.color  # Use the stored color from the client object
            )
        )
        serialized_message = incoming_msg.SerializeToString()
        message_length = struct.pack("<L", len(serialized_message))

        for client in connected_clients:
            if client.client_socket != sender_client_socket:
                try:
                    client.client_socket.sendall(message_length + serialized_message)
                except Exception as e:
                    print(f"[ERROR] Failed to send message to {client.nickname}: {e}")


def client_handler(client_socket, addr):
    try:
        connected = True
        client = ClientConnection(client_socket)
        while connected:
            try:
                client_msg = client.recv_msg()
                print(repr(client_msg))
                message_type = client_msg.WhichOneof("message")
                if message_type == "disconnect":
                    connected = False
                elif message_type == "register":
                    client.set_nickname_and_color(client_msg.register.nickname, client_msg.register.color) #sending the color and nickname together
                    connected_clients.append(client)
                    print(f'[CONNECTED] {client.nickname} connected with color {client.color}.')

                elif message_type == "send":
                    print(f"[{client.nickname}] : {client_msg}")
                    broadcast(client.nickname, client_msg.send, client_socket)

            except Exception as e:
                print(f"[ERROR] {e}")
                connected = False
    finally:
        connected_clients.remove(client)
        client_socket.close()
        print(f'[DISCONNECTED] {client.nickname} ({addr}) disconnected.')

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
