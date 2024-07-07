import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

PORT = 5050
FORMAT = 'utf-8'
HEADER = 64
SERVER = '192.168.56.1'  # Replace with your server's IP address
DISCONNECT_MSG = 'disconnect!'
ADDR = (SERVER, PORT)

# Initialize socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class ChatClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chat Client")

        self.chat_frame = tk.Frame(self.root)
        self.chat_frame.pack(pady=10)

        self.chat_log = tk.Text(self.chat_frame, state=tk.DISABLED, height=20, width=50)
        self.chat_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.chat_frame, command=self.chat_log.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_log.config(yscrollcommand=self.scrollbar.set)

        self.message_input = tk.Entry(self.root, width=50)
        self.message_input.pack(pady=5)

        self.send_button = tk.Button(self.root, text="Send", command=self.send_messages)
        self.send_button.pack(pady=5)

        self.client_name = ""
        self.get_username()
        self.start_connection()

        # Start a thread to handle incoming messages
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def get_username(self):
        self.client_name = simpledialog.askstring("Username", "What's your name?", parent=self.root)
        if not self.client_name:
            messagebox.showerror("Error", "Name cannot be empty")
            self.get_username()
        #want to add feature to choose your message color!

    def start_connection(self):
        try:
            client.connect(ADDR)
            print(f'[CONNECTED] {self.client_name} connected successfully to the server')
            self.send(self.client_name)
        except socket.error as e:
            messagebox.showerror("Error", f"Unable to connect to the server: {e}")
            print(f'[ERROR] Unable to connect {self.client_name} to the server: {e}')
            self.root.quit()

    def send(self, msg):
        try:
            message = msg.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(message)
            self.update_chat_log(f"You: {msg}")
        except Exception as e:
            print(f'[ERROR] {e}')
            messagebox.showerror("Error", "Message sending failed")

    def send_messages(self):
        msg = self.message_input.get()
        if msg:
            if msg == DISCONNECT_MSG:
                self.send(DISCONNECT_MSG)
                client.close()
                self.root.quit()
            else:
                self.send(msg)
            self.message_input.delete(0, tk.END)  # Clear the input field

    def receive_messages(self):
        while True:
            try:
                msg_length = client.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length)
                    msg = client.recv(msg_length).decode(FORMAT)
                    self.update_chat_log(f"Server: {msg}")
            except Exception as e:
                print(f"[ERROR] {e}")
                break

    def update_chat_log(self, msg):
        self.chat_log.config(state=tk.NORMAL)
        self.chat_log.insert(tk.END, f"{msg}\n")
        self.chat_log.yview(tk.END)
        self.chat_log.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = ChatClientApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
