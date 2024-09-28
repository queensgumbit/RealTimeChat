import socket
import threading
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
        #self.chat_pb2 = chat_pb2
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

        self.receive_thread = threading.Thread(target=self.receive_message, daemon=True)
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
        self.color_msg = chat_pb2.ChatProtocol(register=chat_pb2.ClientRegister(nickname=self.client_name, color=self.name_color))
        messagebox.showinfo("Color Selected", f"You have chosen {self.name_color} for your messages.")
        window.destroy()

    def start_connection(self):
        global client
        try:
            client.connect((self.server_ip, self.server_port))
            # Send client name to server upon connection
            msg = chat_pb2.ChatProtocol(register=chat_pb2.ClientRegister(nickname=f"{self.client_name}"))
            self.send(msg)
            print(f'[CONNECTED] {self.client_name} connected successfully to the server')
        except socket.gaierror:
            messagebox.showerror("Error", "Invalid IP address. Please check and try again.")
        except socket.error as e:
            messagebox.showerror("Error", f"Unable to connect to the server: {e}")
            print(f'[ERROR] Unable to connect {self.client_name} to the server: {e}')
            self.root.quit()

    def send(self, msg):
        global client
        if not client:
            print(f"[ERROR] No client connection established")
            return
        try:
            serialized_msg = msg.SerializeToString()
            msg_length = len(serialized_msg)

            # Pack the length as a 32-bit (4 bytes) integer in little-endian format
            packed_msg_length = struct.pack("<L", msg_length)

            client.send(packed_msg_length)
            client.send(serialized_msg)
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
                # send the message with msg and color
                client_msg = chat_pb2.ChatProtocol(
                    send=chat_pb2.ClientSendMsg(msg=msg, color=self.name_color)
                )
                self.send(client_msg)
                incoming_msg = chat_pb2.ClientRecvMsg(msg=msg, sender=self.client_name, color=self.name_color)
                self.update_chat_log(incoming_msg)
            self.message_input.delete(0, ctk.END)

    def receive_message(self):
        global client
        while True:
            try:
                msg_len_bytes = client.recv(4)
                if not msg_len_bytes:
                    break
                msg_len = struct.unpack("<L", msg_len_bytes)[0]
                msg_data = client.recv(msg_len)

                client_msg = chat_pb2.ChatProtocol()
                client_msg.ParseFromString(msg_data)
                print(repr(client_msg))
                message_type = client_msg.WhichOneof("message")
                if message_type == "incoming":
                    self.update_chat_log(client_msg.incoming)
                else:
                    print("UNEXPECTED")

            except Exception as e:
                print(f"[ERROR] {e}")
                break

    def update_chat_log(self, incoming_msg):
        color = incoming_msg.color  # Use the color from the incoming message(went through the protocol)
        message_text = incoming_msg.msg
        sender = incoming_msg.sender

        print(repr(incoming_msg))
        self.chat_log.configure(state=ctk.NORMAL)

        # creating a tag for each sender
        tag_name = f"{sender}_tag"

        # If the tag doesn't already exist, configure it with the specific color
        if not tag_name in self.chat_log.tag_names():
            self.chat_log.tag_config(tag_name, foreground=color)

        self.chat_log.insert(ctk.END, f"{sender}: ", tag_name)
        self.chat_log.insert(ctk.END, f"{message_text}\n")

        self.chat_log.yview(ctk.END)
        self.chat_log.configure(state=ctk.DISABLED)


def main():
    root = ctk.CTk()
    app = ChatClientApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
