import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox
import customtkinter as ctk
from tkinter import Toplevel
import chat_pb2  # Import the generated protobuf classes
import struct
PORT = 5050
FORMAT = 'utf-8'
HEADER = 64
DISCONNECT_MSG = 'disconnect!'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

class ChatClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chatic - Real time chat")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        self.banner_frame = ctk.CTkFrame(self.root)
        self.banner_frame.pack(pady=10)

        self.banner_label = ctk.CTkLabel(self.banner_frame, text="Chatic - Real time chat",
                                         font=('Futura', 30))
        self.banner_label.pack()

        self.chat_frame = ctk.CTkFrame(self.root)
        self.chat_frame.pack(pady=10)

        self.chat_log = ctk.CTkTextbox(self.chat_frame, state=ctk.DISABLED, height=500, width=650)
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
        self.get_username_and_server_info(root)
        self.start_connection()

        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def get_username_and_server_info(self, root):
        dialog_window = Toplevel(root)
        dialog_window.geometry("800x800")
        dialog_window.withdraw()  # Hide the dialog window

        self.client_name = simpledialog.askstring("Username", "What's your name?", parent=dialog_window)
        if not self.client_name:
            messagebox.showerror("Error", "Name cannot be empty")
            self.get_username_and_server_info(root)

        self.server_ip = simpledialog.askstring("Server IP", "Enter the server IP address:", parent=dialog_window)
        self.server_port = simpledialog.askinteger("Server Port", "Enter the server port:", parent=dialog_window)

        if not self.server_ip or not self.server_port:
            messagebox.showerror("Error", "Server IP and port cannot be empty")
            self.get_username_and_server_info(root)

        self.get_color_preference()
        dialog_window.destroy()  # Closing server details and color dialog

    def get_color_preference(self):
        color_window = ctk.CTkToplevel(self.root)
        color_window.title("Choose Your Color")
        color_window.geometry("300x150")

        color_label = ctk.CTkLabel(color_window, text="Choose your name color:", corner_radius=3, text_color="#65a9c2")
        color_label.pack(pady=10)

        color_options = ['red', 'blue', 'green', 'yellow', 'purple', 'orange']
        color_var = ctk.StringVar(value=color_options[0])

        color_menu = ctk.CTkOptionMenu(color_window, variable=color_var, values=color_options)
        color_menu.pack(pady=10)

        confirm_button = ctk.CTkButton(color_window, text="Confirm", command=lambda: self.choose_color(color_var, color_window))
        confirm_button.pack(pady=10)

    def choose_color(self, color_var, window):
        self.name_color = color_var.get()
        messagebox.showinfo("Color Selected", f"You have chosen {self.name_color} for your messages.")
        window.destroy()

    def start_connection(self):
        try:
            #client.connect((self.server_ip, self.server_port))
            #client_hello = chat_pb2.ClientHello(nickname=self.client_name)
            #self.send(client_hello.SerializeToString())
            # Send client name to server upon connection
            msg = chat_pb2.ClientSendMsg(...)
            serialized_msg = msg.SerializeToString()
            socket.send(struct.pack("<L", len(serialized_msg)))
            socket.send(serialized_msg)

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
            msg_length = len(msg)
            send_length = str(msg_length).encode(FORMAT)
            send_length += b' ' * (HEADER - len(send_length))
            client.send(send_length)
            client.send(msg)
        except Exception as e:
            print(f'[ERROR] {e}')
            messagebox.showerror("Error", "Message sending failed")

    def send_messages(self):
        msg = self.message_input.get()
        if msg:
            if msg == DISCONNECT_MSG:
                self.send(DISCONNECT_MSG.encode(FORMAT))
                client.close()
                self.root.quit()
            else:
                client_msg = chat_pb2.ClientSendMsg(msg=f"{self.client_name}: {self.name_color}: {msg}")
                self.send(client_msg.SerializeToString())
                full_msg = f"{self.client_name}: {self.name_color}: {msg}"
                self.update_chat_log(full_msg)  # Update chat log immediately after sending
            self.message_input.delete(0, ctk.END)

    def receive_messages(self):
        while True:
            try:
                msg_length = client.recv(HEADER).decode(FORMAT)
                if msg_length:
                    msg_length = int(msg_length.strip())
                    msg_data = client.recv(msg_length)
                    client_msg = chat_pb2.ClientSendMsg()
                    client_msg.ParseFromString(msg_data)
                    self.update_chat_log(f"{client_msg.msg}")
            except Exception as e:
                print(f"[ERROR] {e}")
                break

    def update_chat_log(self, msg):
        self.chat_log.configure(state=ctk.NORMAL)

        parts = msg.split(": ", 2)
        if len(parts) == 3:
            name, color, message = parts
            self.chat_log.insert(ctk.END, f"{name}: ", name)
            self.chat_log.tag_config(name, foreground=color)
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
