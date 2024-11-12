import tkinter as tk

import os
os.system("defaults write -g NSRequiresAquaSystemAppearance -bool Yes")


class FileSharingApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # window configuration
        self.title("File Sharing Platform")
        self.geometry("800x600")
        self.configure(bg="#2C2C2C")

        # define colors
        self.bg_color = "#2C2C2C"  
        self.sidebar_color = "#3D3D3D"
        self.button_color = "#BB86FC" 
        self.button_hover_color = "#A569BD"
        self.text_color = "white"
        self.online_color = "lime"

        # initialize UI elements
        self.create_sidebar()
        self.create_main_content()


    def create_sidebar(self):
        # sidebar frame
        self.sidebar = tk.Frame(self, width=200, bg=self.sidebar_color, height=500)
        self.sidebar.pack(side="left", fill="y")

        # sidebar buttons
        self.create_sidebar_button("My Files")
        self.create_sidebar_button("All Files")
        self.create_sidebar_button("Performance")
        self.create_sidebar_button("Settings")
        self.create_sidebar_button("Account")

        # status label
        self.status_label = tk.Label(
            self.sidebar,
            text="Status: Online",
            font=("Arial", 14),
            fg=self.online_color,
            bg=self.sidebar_color
        )


    def create_sidebar_button(self, text):
        button = tk.Button(
            self.sidebar,
            text=text,
            font=("Arial", 14),
            fg=self.text_color,
            highlightbackground=self.button_color,
            activebackground=self.button_hover_color,
            bd=0,
            relief="flat",
            padx=10,
            pady=10
        )
        button.pack(pady=10, fill="x")

    def create_main_content(self):
        self.main_content = tk.Frame(self, bg=self.bg_color)
        self.main_content.pack(expand=True, fill="both")

        # section title
        self.title_label = tk.Label(
            self.main_content,
            text="My Files",
            font=("Arial", 24),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.title_label.pack(pady=20)



if __name__ == "__main__":
    app = FileSharingApp()
    app.mainloop()