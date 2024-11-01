import tkinter as tk
from tkinter import ttk

import sv_ttk

class App(tk.Frame):
    def __init__(self, root):
        self.root = root
        self.root.title("Client")
        self.root.geometry("800x700")

        self.canvas = tk.Canvas(self.root, width=800, height=700)
        self.canvas.pack()

        self.canvas.create_rectangle(350, 100, 450, 600, fill="white")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    sv_ttk.set_theme("dark")
    root.mainloop()
