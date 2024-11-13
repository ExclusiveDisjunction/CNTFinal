import tkinter as tk
import socket
from tkinter import font as tkFont
from tkinter import messagebox
import bcrypt

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
        self.button_color = "#BB86FC" 
        self.button_hover_color = "#A569BD"
        self.text_color = "white"
        self.online_color = "lime"

        # initialize UI elements
        self.current_page = None
        self.pages = {}

        self.create_sidebar()
        self.create_pages()

        self.show_page("Connect")

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
            text="Status: Online",
            font=("Figtree", 14),
            fg="lime",
            bg=self.sidebar_color
        )
        self.status_label.pack(pady=20)

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
        label = tk.Label(self, text="My Files:", font=("Figtree", 24), fg=self.text_color, bg=self.bg_color)
        label.pack(pady=20)
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

    def hash_password(plain_password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode(), salt)
        return hashed_password

    def validate_login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()

        hashed_password = self.hash_password(self.password)



        # psuedocode
        # connection is already made with server... done on initailization
        # user inputs login creditions
        # password is hashed
        
        # send username and hashed password to server, validate credentials
        # if valid,
        #  go to My Files page
        # else
        #  show error message

    def create_connection(self, ip_address, port):
        raise NotImplementedError("Subclasses should implement this method.")
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # server_address = (ip_address, port)

        # try:
        #     client_socket.connect(server_address)
        #     login_message = f"LOGIN {self.username} {self.password}" # however the format is
        #     client_socket.send(login_message.encode())

        #     response = client_socket.recv(1024).decode()
        #     if "SUCCESS" in response:
        #         self.master.show_my_files()
        #     else:
        #         messagebox.showerror("Error", "Invalid username or password.")

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



if __name__ == "__main__":
    app = FileSharingApp()
    app.mainloop()