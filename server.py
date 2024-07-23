import socket
import threading

SERVER = '192.168.1.106'
PORT = 5050
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = 'disconnect!'

class ClientConnection:
    def __init__(self, client_socket, nickname):
        self.client_socket = client_socket
        self.nickname = nickname

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
connected_clients = []

def broadcast(message, sender_client_socket):
    print(f"[BROADCASTING] Broadcasting message: {message}")
    for client in connected_clients:
        if client.client_socket != sender_client_socket:
            try:
                message_length = len(message)
                send_length = str(message_length).encode(FORMAT)
                send_length += b' ' * (HEADER - len(send_length))
                client.client_socket.send(send_length)
                client.client_socket.send(message.encode(FORMAT))
                print(f"[SENT] Message sent to {client.nickname}")
            except Exception as e:
                print(f"[ERROR] Failed to send message to {client.nickname}: {e}")

def client_handler(client_socket, addr):
    try:
        client_name_length = client_socket.recv(HEADER).decode(FORMAT)
        client_name = client_socket.recv(int(client_name_length)).decode(FORMAT)
        new_client = ClientConnection(client_socket, client_name)
        connected_clients.append(new_client)
        print(f'[CONNECTED] {client_name} is connected.')

        connected = True
        while connected:
            try:
                msg_length = client_socket.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = client_socket.recv(msg_length).decode(FORMAT)
                    if msg == DISCONNECT_MSG:
                        connected = False
                    else:
                        print(f"[{client_name}] : {msg}")
                        broadcast(msg, client_socket)
            except Exception as e:
                print(f"[ERROR] {e}")
                connected = False
    finally:
        connected_clients.remove(new_client)
        client_socket.close()
        print(f'[DISCONNECTED] {client_name} ({addr}) disconnected.')

def bindServer():
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
    bindServer()
    start_listening()

if __name__ == '__main__':
    main()
