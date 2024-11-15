import threading
import time
import tkinter as tk
import socket
from tkinter import font as tkFont
from tkinter import messagebox
import bcrypt
from Common.message_handler import MessageBasis, AckMessage, ConnectMessage, CloseMessage
import json

class FileSharingApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # window configuration
        self.title("File Sharing Platform")
        self.geometry("1000x800")
        self.configure(bg="#2C2C2C")

        # load fonts
        self.figtree_font = tkFont.Font(family="Figtree", size=14)

        # define colors
        self.bg_color = "#2C2C2C"  
        self.sidebar_color = "#3D3D3D"
        self.topbar_color = "#545454"
        self.button_color = "#BB86FC" 
        self.button_hover_color = "#A569BD"
        self.text_color = "white"
        self.online_color = "lime"
        self.offline_color = "red"

        # initialize UI elements
        self.current_page = None
        self.pages = {}
        self.create_sidebar()
        self.create_pages()

        self.show_page("Connect")

    def create_topbar(self, text=None):
        if hasattr(self, 'topbar'):
            self.title_label.config(text=text)
        else:
            
            self.topbar = tk.Frame(self, height=100, bg=self.topbar_color)
            self.topbar.pack(side="top", fill="x")
            self.title_label = tk.Label(
                self.topbar,
                text=text,
                font=("Figtree", 24),
                fg=self.text_color,
                bg=self.topbar_color,
                justify="left"
            )
            self.title_label.pack()

    def create_sidebar(self):
        self.sidebar = tk.Frame(self, width=200, bg=self.sidebar_color)
        self.sidebar.pack(side="left", fill="y")
        self.buttons = {}
        self.create_sidebar_button("My Files", self.show_my_files, padding=(75, 10))
        self.create_sidebar_button("All Files", self.show_all_files)
        self.create_sidebar_button("Performance", self.show_performance)
        
        self.create_sidebar_button("Settings", self.show_settings, padding=(375,10))
        self.create_sidebar_button("Connect", self.show_connect)

        self.status_label = tk.Label(
            self.sidebar,
            text="Status: ...",
            font=("Figtree", 14),
            fg="gray",
            bg=self.sidebar_color
        )
        self.status_label.pack(pady=20)
        self.create_topbar()

    def create_sidebar_button(self, text, command, padding=(10, 10)):
        button = tk.Button(self.sidebar, text=text, font=("Figtree", 14), bg=self.button_color, fg=self.text_color, command=command)
        button.pack(fill="x", pady=padding)
        self.buttons[text] = button

    def create_pages(self):
        # Instantiate the pages
        self.pages["My Files"] = MyFilesPage(self, self.bg_color, self.text_color, self.button_color)
        self.pages["All Files"] = AllFilesPage(self, self.bg_color, self.text_color, self.button_color)
        self.pages["Performance"] = PerformancePage(self, self.bg_color, self.text_color, self.button_color)
        
        self.pages["Settings"] = SettingsPage(self, self.bg_color, self.text_color, self.button_color)
        self.pages["Connect"] = ConnectPage(self, self.bg_color, self.text_color, self.button_color)


    def show_page(self, page_name):
        if page_name not in self.pages:
            print(f"Error: {page_name} does not exist.")
            return  # Exit early if the page is not found

        # If current_page exists, hide it
        if self.current_page:
            self.current_page.pack_forget()

        # Get the page and show it
        self.current_page = self.pages[page_name]
        self.current_page.pack(expand=True, fill="both")
        self.current_page.load_content()

    def show_my_files(self):
        self.show_page("My Files")
    
    def show_all_files(self):
        self.show_page("All Files")

    def show_performance(self):
        self.show_page("Performance")

    def show_settings(self):
        self.show_page("Settings")

    def show_connect(self):
        self.show_page("Connect")

    def select_button(self, button, command):
        if self.current_button:
            self.current_button.config(bg=self.button_color)
        self.current_button = self.buttons[button]
        self.current_button.config(bg=self.button_hover_color)
        command()

    def status_update(self, status):
        if status == "Online":
            self.status_label.config(fg=self.online_color)
            self.status_label.config(text=f"Status: {status}")
        else:
            self.status_label.config(fg=self.offline_color)
            self.status_label.config(text=f"Status: {status}")

class Page(tk.Frame):
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg=bg_color)
        self.bg_color = bg_color
        self.text_color = text_color
        self.button_color = button_color
        self.content_loaded = False

    def load_content(self):
        if self.content_loaded:
            self.reset_content()
        else:
            print(f"Loading content for {self.__class__.__name__} page.")
        self.content_loaded = True
        self.create_content()

    def reset_content(self):
        for widget in self.winfo_children():
            widget.destroy()

    def create_content(self):
       
        raise NotImplementedError("Subclasses should implement this method.")

class MyFilesPage(Page):
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)

    def create_content(self):
        self.master.create_topbar("My Files")
        file_list = tk.Listbox(self, height=10, width=40)
        file_list.insert(tk.END, "File 1")
        file_list.insert(tk.END, "File 2")
        file_list.insert(tk.END, "File 3")
        file_list.pack(pady=10)

class AllFilesPage(Page):
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)

    def create_content(self):
        raise NotImplementedError("Subclasses should implement this method.")
        

class PerformancePage(Page):
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)

    def create_content(self):
       raise NotImplementedError("Subclasses should implement this method.")

class SettingsPage(Page):
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)

    def create_content(self):
        raise NotImplementedError("Subclasses should implement this method.")

    def save_settings(self, setting):
        print(f"Setting saved: {setting}")

class ConnectPage(Page):
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)
        self.username = ""
        self.password = ""
        self.con = None
        self.server_ip = "127.0.0.1"
        self.server_port = 8081
        self.load_content()
        self.create_connection()

    def hash_password(self, plain_password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode(), salt)
        return hashed_password

    def validate_login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        hashed_password = self.hash_password(self.password)

        connect_message = ConnectMessage(username=self.username, passwordHash=hashed_password.decode())
        try:
            self.con.sendall(connect_message.construct_message_json().encode())

            contents = self.con.recv(1024)
            if contents is None or len(contents) == 0:
                print("Connection terminated")
                messagebox.showerror("Error", "Invalid credentials.")
                self.con.close()
            
            message = MessageBasis.parse_from_json(contents.decode("utf-8"))
            if not isinstance(message, AckMessage):
                print(f"Unexpected message of type {message.message_type()}")
                self.con.close()
                print("Closing connection")
                self.con.send(CloseMessage().construct_message_json().encode())

            message = MessageBasis.parse_from_json(contents.decode("utf-8"))
            if not isinstance(message, AckMessage):
                messagebox.showerror("Error", f"Unexpected message of type {message.message_type()}")
                print(f"Unexpected message of type {message.message_type()}")
                self.con.close()
            self.master.status_update("Online")
            self.master.show_page("My Files")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    def create_connection(self):
        try:
            self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.con.connect((self.server_ip, self.server_port))
            self.master.status_update("Online")
        except Exception as e:
            print(f"Error: {e}")
            if self.con:
                self.con.close()
            self.master.status_update("Offline")

    def load_content(self):

        self.reset_content()

        label = tk.Label(self, text="Please Login:", font=("Figtree", 24), fg=self.text_color, bg=self.bg_color)
        label.pack(pady=20)

        self.username_label = tk.Label(self, text="Username:", font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.username_label.pack(pady=10)

        self.username_entry = tk.Entry(self, font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.username_entry.pack(pady=10)

        self.password_label = tk.Label(self, text="Password:", font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.password_label.pack(pady=10)

        self.password_entry = tk.Entry(self, font=("Figtree", 14), fg=self.text_color, bg=self.bg_color, show="*")
        self.password_entry.pack(pady=10)

        self.login_button = tk.Button(self, text="Login", font=("Figtree", 14), bg=self.button_color, fg=self.text_color, command=self.validate_login)
        self.login_button.pack(pady=10)