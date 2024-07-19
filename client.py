import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
import customtkinter as ctk

PORT = 5050
FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MSG = 'disconnect!'

client = None  

used_colors = set()  # To keep track of used colors

class ChatClientApp:
    def __init__(self, root):
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.root = root
        self.root.title("Chatic - real time chat")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.chat_frame = ctk.CTkFrame(self.root)
        self.chat_frame.pack(pady=90)

        self.chat_log = ctk.CTkTextbox(self.chat_frame, state=ctk.DISABLED, height=400, width=600)
        self.chat_log.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.scrollbar = ctk.CTkScrollbar(self.chat_frame, command=self.chat_log.yview)
        self.scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.chat_log.configure(yscrollcommand=self.scrollbar.set)

        self.message_input = ctk.CTkEntry(self.root, width=600)
        self.message_input.pack(pady=5)

        self.send_button = ctk.CTkButton(self.root, text="Send", command=self.send_messages)
        self.send_button.pack(pady=5)

        self.client_name = ""
        self.name_color = "white"  # Default color
        self.server_ip = ""
        self.server_port = None
        self.get_usernameAndServerInfo(root)

        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def get_usernameAndServerInfo(self, root):
        self.client_name = simpledialog.askstring("Username", "What's your name?", parent=root)
        if not self.client_name:
            messagebox.showerror("Error", "Name cannot be empty")
            self.get_usernameAndServerInfo(root)

        self.server_ip = simpledialog.askstring("Server IP", "Enter the server IP address:", parent=root)
        self.server_port = simpledialog.askinteger("Server Port", "Enter the server port:", parent=root)

        if not self.server_ip or not self.server_port:
            messagebox.showerror("Error", "Server IP and port cannot be empty")
            self.get_usernameAndServerInfo(root)

        self.get_color_preference()

    def get_color_preference(self):
        color_window = ctk.CTkToplevel(self.root)
        color_window.title("Choose Your Color")
        color_window.geometry("300x150")

        color_label = ctk.CTkLabel(color_window, text="Choose your name color:")
        color_label.pack(pady=10)

        available_colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
        color_options = [color for color in available_colors if color not in used_colors]
        color_var = ctk.StringVar(value=color_options[0])

        color_menu = ctk.CTkOptionMenu(color_window, variable=color_var, values=color_options)
        color_menu.pack(pady=10)

        confirm_button = ctk.CTkButton(color_window, text="Confirm", command=lambda: self.set_color_and_connect(color_var.get(), color_window))
        confirm_button.pack(pady=10)

    def set_color_and_connect(self, color, window):
        self.name_color = color
        used_colors.add(color)
        window.destroy()
        self.start_connection()

    def start_connection(self):
        global client
        if client is None or client.fileno() == -1:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((self.server_ip, self.server_port))
            self.send(self.client_name)
            print(f'[CONNECTED] {self.client_name} connected successfully to the server')
        except socket.gaierror:
            messagebox.showerror("Error", "Invalid IP address. Please check and try again.")
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
                self.update_chat_log(full_msg)
            self.message_input.delete(0, ctk.END)

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
        self.chat_log.configure(state=ctk.NORMAL)

        parts = msg.split(": ", 1)
        if len(parts) == 2:
            name, message = parts
            self.chat_log.insert(ctk.END, f"{name}: ", name)
            self.chat_log.tag_config(name, foreground=self.name_color)
            self.chat_log.insert(ctk.END, f"{message}\n")
        else:
            self.chat_log.insert(ctk.END, msg + "\n")

        self.chat_log.yview(ctk.END)
        self.chat_log.configure(state=ctk.DISABLED)

def main():
    root = ctk.CTk()
    app = ChatClientApp(root)
    root.mainloop()

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    root = tk.Tk()
    app = ChatClientApp(root)
