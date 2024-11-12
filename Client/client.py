import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk, ImageFont
import os

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

        self.show_page("My Files")

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
        # Implement specific content loading logic here
        self.create_content()

    def reset_content(self):
        for widget in self.winfo_children():
            widget.destroy()  # Remove all widgets from the page

    def create_content(self):
       
        raise NotImplementedError("Subclasses should implement this method.")

class MyFilesPage(Page):
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)

    def create_content(self):
        label = tk.Label(self, text="Here are my files:", font=("Figtree", 24), fg=self.text_color, bg=self.bg_color)
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

    def validate_login(self, username, password):
        print(f"Logging in with username: {username} and password: {password}")

    def create_connection(self, ip_address, port):
        print(f"Connecting to {ip_address} on port {port}")

    def load_content(self):
        raise NotImplementedError("load_content() must be implemented by subclasses")

if __name__ == "__main__":
    app = FileSharingApp()
    app.mainloop()