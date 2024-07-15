import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

PORT = 5050
FORMAT = 'utf-8'
HEADER = 64
SERVER = '192.168.56.1'  
DISCONNECT_MSG = 'disconnect!'
ADDR = (SERVER, PORT)

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
        self.name_color = "black"  # Default color
        self.get_username(root)
        self.start_connection()

        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def get_username(self, root):
        self.client_name = simpledialog.askstring("Username", "What's your name?", parent=self.root)
        if not self.client_name:
            messagebox.showerror("Error", "Name cannot be empty")
            self.get_username(root)

        option_list = ['red', 'blue', 'purple', 'yellow']
        self.value_inside = tk.StringVar(root)
        self.value_inside.set(option_list[0])
        self.question_menu = tk.OptionMenu(root, self.value_inside, *option_list)
        self.question_menu.pack()

        self.confirm_button = tk.Button(root, text="Confirm Color", command=self.choose_color)
        self.confirm_button.pack(pady=5)

    def choose_color(self):
        self.name_color = self.value_inside.get()
        messagebox.showinfo("Color Selected", f"You have chosen {self.name_color} for your messages.")

    def start_connection(self):
        try:
            client.connect(ADDR)
            self.send(self.client_name)  # Send client name to server upon connection
            print(f'[CONNECTED] {self.client_name} connected successfully to the server')
        except socket.error as e:
            messagebox.showerror("Error", f"Unable to connect to the server: {e}")
            print(f'[ERROR] Unable to connect {self.client_name} to the server: {e}')
            self.root.quit()

    def send(self, msg):
        if not client:
            print(f"[ERROR] No client connection established")
            return

        try:
            message = msg.encode(FORMAT)
            msg_length = len(message)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(message)
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
                full_msg = f"{self.client_name}: {msg}"
                self.send(full_msg)
                self.update_chat_log(full_msg)  # Update chat log immediately after sending
            self.message_input.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                msg_length = client.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length.strip())
                    msg = client.recv(msg_length).decode(FORMAT)
                    self.update_chat_log(f"{msg}")
            except Exception as e:
                print(f"[ERROR] {e}")
                break

    def update_chat_log(self, msg):
        self.chat_log.config(state=tk.NORMAL)

        parts = msg.split(": ", 1)
        if len(parts) == 2:
            name, message = parts
            self.chat_log.insert(tk.END, f"{name}: ", name)
            self.chat_log.tag_config(name, foreground=self.name_color)
            self.chat_log.insert(tk.END, f"{message}\n")
        else:
            self.chat_log.insert(tk.END, msg + "\n")

        self.chat_log.yview(tk.END)
        self.chat_log.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = ChatClientApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()
