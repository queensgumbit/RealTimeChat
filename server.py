import socket
import threading

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = 'disconnect!'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
connected_clients = []

def broadcast(message, sender_client):
    print(f"[BROADCASTING] Broadcasting message: {message}")
    for client_socket, client_name in connected_clients:
        if client_socket != sender_client:
            try:
                message_length = len(message)
                send_length = str(message_length).encode(FORMAT)
                send_length += b' ' * (HEADER - len(send_length))
                client_socket.send(send_length)
                client_socket.send(message.encode(FORMAT))
                print(f"[SENT] Message sent to {client_name}")
            except Exception as e:
                print(f"[ERROR] Failed to send message to {client_name}: {e}")

def client_handler(client_socket, addr):
    client_name_length = client_socket.recv(HEADER).decode(FORMAT)
    client_name = client_socket.recv(int(client_name_length)).decode(FORMAT)
    connected_clients.append((client_socket, client_name))
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

    connected_clients.remove((client_socket, client_name))
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
