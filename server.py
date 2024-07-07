import socket
import threading


SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5050
#MEMBERS = 4
HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MSG = 'disconnect!'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
connected_clients = []   #list of all connected clients in form of tuple (addr,client_name)

def client_handler(client, addr):
    client_name_length = client.recv(HEADER).decode(FORMAT)
    client_name = client.recv(int(client_name_length)).decode(FORMAT)
    connected_clients.append((addr, client_name))
    print(f'[CONNECTED] {client_name} is connected.')
    connected = True
    while connected:
        msg_length = client.recv(HEADER).decode(FORMAT)
        if msg_length:
            try:
                msg_length = int(msg_length)
                msg = client.recv(msg_length).decode(FORMAT)
                if msg == DISCONNECT_MSG:
                    connected = False
                print(f"[{client_name}] : {msg}")
            except ValueError:
                print(f"[ERROR] Invalid message length received from {addr}")
        else:
            connected = False
    connected_clients.remove((addr, client_name))
    client.close()
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
        client, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(client, addr))
        thread.start()
        print(f"\n[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

def main():
    bindServer()
    start_listening()

if __name__ == '__main__':
    main()