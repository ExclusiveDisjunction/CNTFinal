import os
import threading
import tkinter as tk
import socket
from tkinter import font as tkFont
from tkinter import messagebox, filedialog
from tkinter import simpledialog
from tkinter import colorchooser
from tkmacosx import Button
import hashlib
from Common.message_handler import *
from Common.file_io import FileInfo, get_file_type, FileType, read_file_for_network, DirectoryInfo, receive_network_file_binary, receive_network_file

class FileSharingApp(tk.Tk):
    """
    Main application window for the file sharing platform.
    Inherits from tk.Tk to create the root window.
    """
    def __init__(self):
        super().__init__()
        
        # socket connection instance
        self.con = None

        # window configuration
        self.title("File Sharing Platform")
        self.geometry("900x700")
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
        
        self.theme = {
            "bg_color": "#2C2C2C",
            "text_color": "white",
            "button_color": "#BB86FC",
            "sidebar_color": "#3D3D3D",
            "topbar_color": "#545454"
        }

        # initialize UI elements
        self.current_page = None
        self.pages = {}
        self.buttons = {}

        self.create_sidebar()
        self.create_pages()
        self.show_page("Connect")
        
    def update_theme(self, bg_color, text_color, button_color):
        self.theme.update({
            "bg_color": bg_color,
            "text_color": text_color,
            "button_color": button_color
        })
        self.apply_theme()
    
    # apply theme to all widgets
    def apply_theme(self):
        # Update main window
        self.configure(bg=self.theme["bg_color"])
        
        # Update sidebar
        if hasattr(self, 'sidebar'):
            self.sidebar.configure(bg=self.theme["sidebar_color"])
            self.status_label.configure(bg=self.theme["sidebar_color"], fg=self.theme["text_color"])
            
        # Update topbar
        if hasattr(self, 'topbar'):
            self.topbar.configure(bg=self.theme["topbar_color"])
            self.title_label.configure(bg=self.theme["topbar_color"], fg=self.theme["text_color"])
            
        # Update buttons
        for button in self.buttons.values():
            button.configure(bg=self.theme["button_color"], fg=self.theme["text_color"])
            
        # Update all pages
        for page in self.pages.values():
            page.update_theme(self.theme)
            
    # create topbar
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

    # create sidebar
    def create_sidebar(self):
        self.sidebar = tk.Frame(self, width=200, bg=self.sidebar_color)
        self.sidebar.pack(side="left", fill="y")

        self.buttons["My Files"] = self.create_sidebar_button("My Files", self.show_my_files, padding=(75, 10), stateE=tk.DISABLED)
        self.buttons["Performance"] = self.create_sidebar_button("Performance", self.show_performance, stateE=tk.DISABLED)
        
        self.buttons["Settings"] = self.create_sidebar_button("Settings", self.show_settings, padding=(375,10), stateE=tk.DISABLED)
        self.buttons["Connect"] = self.create_sidebar_button("Connect", self.show_connect)

        self.status_label = tk.Label(
            self.sidebar,
            text="Status: ...",
            font=("Figtree", 14),
            fg="gray",
            bg=self.sidebar_color
        )
        self.status_label.pack(pady=20)
        self.create_topbar()

    # create sidebar button
    def create_sidebar_button(self, text, command, padding=(10, 10), stateE=tk.NORMAL):
        button = Button(self.sidebar, text=text, font=("Figtree", 14), bg=self.button_color, fg=self.text_color, state=stateE, command=command, borderless=1)
        button.pack(fill="x", pady=padding)
        return button

    # create pages
    def create_pages(self):
        # Instantiate the pages
        self.pages["My Files"] = MyFilesPage(self, self.bg_color, self.text_color, self.button_color)
        self.pages["Performance"] = PerformancePage(self, self.bg_color, self.text_color, self.button_color)
        
        self.pages["Settings"] = SettingsPage(self, self.bg_color, self.text_color, self.button_color)
        self.pages["Connect"] = ConnectPage(self, self.bg_color, self.text_color, self.button_color)

    # enable buttons depending on state of application
    def enable_buttons(self):
        if "Connect" in self.buttons:
            self.buttons["Connect"].config(state=tk.DISABLED)
        for button in self.buttons.values():
            if button is not None:
                button.config(state=tk.NORMAL)

    # show specific pages
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
        
    # update status label
    def status_update(self, status):
        if status == "Online":
            self.status_label.config(fg=self.online_color)
            self.status_label.config(text=f"Status: {status}")
        else:
            self.status_label.config(fg=self.offline_color)
            self.status_label.config(text=f"Status: {status}")
    
    # update colors for all pages
    def update_colors(self, background, text, button):
        self.bg_color = background
        self.text_color = text 
        self.button_color = button
        # update all pages
        for page in self.pages.values():
            if hasattr(page, '_update_page_colors'):
                page._update_page_colors()

class Page(tk.Frame):
    """
    Base class for all pages in the application.
    Provides common functionality for theme management and content loading.
    """
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg=bg_color)
        self.bg_color = bg_color
        self.text_color = text_color
        self.button_color = button_color
        self.content_loaded = False

    # loads content
    def load_content(self):
        if self.content_loaded:
            self.reset_content()
        else:
            print(f"Loading content for {self.__class__.__name__} page.")
        self.content_loaded = True
        self.create_content()

    #updates themes for pages
    def update_theme(self, theme):
        self.bg_color = theme["bg_color"]
        self.text_color = theme["text_color"]
        self.button_color = theme["button_color"]
        self.configure(bg=self.bg_color)
        self.apply_theme_to_widgets()
    
    # applys themes to widgets
    def apply_theme_to_widgets(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(bg=self.bg_color, fg=self.text_color)
            elif isinstance(widget, Button):
                widget.configure(bg=self.button_color, fg=self.text_color)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self.bg_color)
                for child in widget.winfo_children():
                    if isinstance(child, tk.Label):
                        child.configure(bg=self.bg_color, fg=self.text_color)
                    elif isinstance(child, Button):
                        child.configure(bg=self.button_color, fg=self.text_color)

    # reset content
    def reset_content(self):
        for widget in self.winfo_children():
            widget.destroy()

class MyFilesPage(Page):
    """
    Page for displaying and managing user's files.
    Handles file upload, download, deletion and navigation through directories.
    """
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)
        self.current_dir = None
    
    # creates content
    def create_content(self):
        self.master.create_topbar("My Files")

        # Adds a label to display the current path
        self.path_label = tk.Label(
            self,
            text="Path: /",
            font=("Figtree", 12),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.path_label.pack(pady=(5,0))
        
        # Create a frame to hold ".." and "Open Folder" buttons
        nav_frame = tk.Frame(self, bg=self.bg_color)
        nav_frame.pack(pady=5)

        # Adds button to go up directory
        up_dir_button = Button(
            nav_frame,
            text="..",
            command=self.move_up_directory,
            font=("Figtree", 12),
            bg=self.button_color,
            fg=self.text_color,
            borderless=1
        )
        up_dir_button.pack(side=tk.LEFT, padx=5)

        # Adds the "Open Folder" button next to ".."
        self.open_folder_button = Button(
            nav_frame,
            text="Open Folder",
            command=self.open_selected_folder,
            font=("Figtree", 12),
            bg=self.button_color,
            fg=self.text_color,
            borderless=1,
            state=tk.DISABLED  # Initially disabled
        )
        self.open_folder_button.pack(side=tk.LEFT, padx=5)

        self.file_list = tk.Listbox(self, height=20, width=80, selectforeground=self.text_color, selectbackground=self.button_color, font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.file_list.pack(pady=10)
        self.file_list.bind("<<ListboxSelect>>", self.on_file_select)
        # self.file_list.bind("<Double-Button-1>", self.on_double_click) # Currently not working

        button_frame = tk.Frame(self, bg=self.bg_color)
        button_frame.pack(pady=10)

        self.upload_button = Button(button_frame, text="Upload File", command=self.upload_files, font=("Figtree", 14), bg=self.button_color, fg=self.text_color, borderless=1)
        self.upload_button.pack(side=tk.LEFT, padx=10)

        self.download_button = Button(button_frame, text="Download File", command=self.download_files, font=("Figtree", 14), bg=self.button_color, fg=self.text_color, borderless=1, state=tk.DISABLED)
        self.download_button.pack(side=tk.RIGHT, padx=10)

        self.delete_button = Button(button_frame, text="Delete File", command=self.delete_files, font=("Figtree", 14), bg=self.button_color, fg=self.text_color, borderless=1, state=tk.DISABLED)
        self.delete_button.pack(side=tk.RIGHT, padx=10)

        self.create_subfolder_button = Button(nav_frame, text="Create Subfolder", command=self.create_subfolder, font=("Figtree", 14), bg=self.button_color, fg=self.text_color, borderless=1)
        self.create_subfolder_button.pack(side=tk.RIGHT, padx=10)
        
        self.delete_subfolder_button = Button(nav_frame, text="Delete Subfolder", command=self.delete_subfolder, font=("Figtree", 14), bg=self.button_color, fg=self.text_color, borderless=1)
        self.delete_subfolder_button.pack(side=tk.RIGHT, padx=10)

        self.request_files()
    
    # opens selected folder
    def open_selected_folder(self, event=None):
        try:
            selected_indices = self.file_list.curselection()
            if not selected_indices:
                return

            selected_index = selected_indices[0]
            selected_item = self.file_list.get(selected_index)
            
            if selected_item.endswith(" (d)"):
                item_name = selected_item[:-4]  # Removes the last 4 characters " (d)"
                self.move_directory(item_name)
            else:
                self.show_error("Selected item is not a directory.")

        except Exception as e:
            self.show_error(f"Error handling double-click: {e}")

    # requests files from server
    def request_files(self):
        dir_message = DirMessage()
        try:
            if self.master.con is None:
                print("No connection")
                return
            
            self.master.con.sendall(dir_message.construct_message_json().encode())

            dir_resp = MessageBasis.parse_from_json(self.master.con.recv(1024).strip(b'\x00').decode("utf-8"))
            code, message, curr, size = dir_resp.code(), dir_resp.message(), dir_resp.curr_dir(), dir_resp.size()
            
            self.current_dir = curr
            
            self.master.con.sendall(AckMessage(200, "OK").construct_message_json().encode())
            
            if code == 200:
                dir_struct_data = receive_network_file_binary(self.master.con, size).decode("utf-8")
                dir_struct = DirectoryInfo.from_dict(json.loads(dir_struct_data))
                self.display_files(dir_struct)
                
                # Update path display
                path_text = f"Path: /{self.current_dir}" if self.current_dir else "Path: /"
                self.path_label.config(text=path_text)
            else:
                print(f"Failed to get directory structure because: {message}")  
        except Exception as e:
            print(f"Error: {e}")

    # displays files
    def display_files(self, dir_info):
        self.file_list.delete(0, tk.END)
        for item in dir_info.contents():
            if isinstance(item, FileInfo):
                self.file_list.insert(tk.END, f"{item.name()} (f)")
            elif isinstance(item, DirectoryInfo):
                self.file_list.insert(tk.END, f"{item.name()} (d)")

    # thread for uploading files
    def upload_files(self):
        threading.Thread(target=self._upload_files).start()

    # uploads files from client to server
    def _upload_files(self):
        file_path = filedialog.askopenfilename()
        if file_path is None or len(file_path) == 0:
            return
        
        file_name = os.path.basename(file_path)
        file_contents = read_file_for_network(Path(file_path))
        file_kind = get_file_type(Path(file_name))

        upload_message = UploadMessage(Path(file_name), file_kind, len(file_contents))

        try:
            self.master.con.sendall(upload_message.construct_message_json().encode())

            ack_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            if not ack_resp:
                self.show_error("No response from server.")
                return
            print(ack_resp)
            ack_message = MessageBasis.parse_from_json(ack_resp)
            if not isinstance(ack_message, AckMessage):
                self.show_error(f"Unexpected message of type {ack_message.message_type()}")
                return
            
            if ack_message.code() == 200:
                self.send_file_data(file_contents)
            else:
                self.show_error(f"Server responded with code E: {ack_message.code()}: {ack_message.message()}")
        except Exception as e:
            self.show_error(f"Error: {e}")

    # gets file kind
    def get_file_kind(self, file_name) -> FileType:
        return get_file_type(Path(file_name))
    
    # sends file data to server
    def send_file_data(self, file_contents):
        try:
            sent_count = 0
            for item in file_contents:
                self.master.con.send(item)
                sent_count += 1
                
            if sent_count != len(file_contents):
                self.show_error("Failed to send all file contents.")
                return
            
            final_ack_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            if not final_ack_resp:
                self.show_error("No response from server.")
                return
            
            final_ack_message = MessageBasis.parse_from_json(final_ack_resp)
            if not isinstance(final_ack_message, AckMessage):
                self.show_error(f"Unexpected message of type {final_ack_message.message_type()}")
                return
            
            if final_ack_message.code() == 200:
                self.after(0, lambda: messagebox.showinfo("Success", "File uploaded successfully."))
                # refresh file list
                self.after(0, self.request_files)

            else:
                self.show_error(f"Server responded with code {final_ack_message.code()}: {final_ack_message.message()}")

        except Exception as e:
            self.show_error(f"Error Test2: {e}")  

    # thread for downloading files
    def download_files(self):
        threading.Thread(target=self._download_files).start()

    # downloads files from server
    def _download_files(self):
        try:
            selected_file = self.file_list.get(self.file_list.curselection())
            if not selected_file:
                return
                
            file_name = selected_file.split(" ")[0].strip()
            
            save_path = filedialog.asksaveasfilename(
                defaultextension=Path(file_name).suffix,
                initialfile=file_name
            )
            if not save_path:
                return
                            
            self.master.con.sendall(DownloadMessage(file_name).construct_message_json().encode())
            
            download_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            download_message = MessageBasis.parse_from_json(download_resp)
            
            if download_message and isinstance(download_message, DownloadMessage):
                if download_message.status() == 200:
                    self.master.con.sendall(AckMessage(200, "OK").construct_message_json().encode())
                    size = download_message.size()
                    
                    if receive_network_file(Path(save_path), self.master.con, size):
                        self.master.con.sendall(AckMessage(200, "OK").construct_message_json().encode())
                        messagebox.showinfo("Success", "File downloaded successfully")
                    else:
                        self.master.con.sendall(AckMessage(400, "File transfer failed").construct_message_json().encode())
                        messagebox.showerror("Error", "File transfer failed")
                else:
                    messagebox.showerror("Error", f"Download failed: {download_message.message()}")
        except Exception as e:
            messagebox.showerror("Error", f"Download error: {str(e)}")
            self.clear_socket_buffer()

    # thread for deleting files
    def delete_files(self):
        threading.Thread(target=self._delete_files).start()

    # deletes files from server
    def _delete_files(self):
        try:
            selected_file = self.file_list.get(self.file_list.curselection())
            if selected_file is None or len(selected_file) == 0:
                return
            file_name = selected_file.split(" ")[0].strip()
            self.master.con.sendall(DeleteMessage(file_name).construct_message_json().encode())

            delete_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            delete_message = MessageBasis.parse_from_json(delete_resp)
            if delete_message is not None and isinstance(delete_message, AckMessage):
                if delete_message.code() == 200:
                    self.after(0, lambda: messagebox.showinfo("Success", "File deleted successfully."))
                    self.after(0, self.request_files)
                else:
                    self.after(0, lambda: messagebox.showinfo("Failure", f"Failed to delete file because: {delete_message.message()}"))
            self.after(0, self.update_button_states)
        except Exception as e:
            print(f"Error: {e}")

    # thread for creating subfolder
    def create_subfolder(self):
        folder_name = simpledialog.askstring("Create Subfolder", "Enter the name of the subfolder:")
        if folder_name is not None or len(folder_name.strip()) > 0:
            threading.Thread(target=self._create_subfolder(folder_name)).start()

    # creates subfolder on server
    def _create_subfolder(self, folder_name):
        try:
            self.master.con.sendall(SubfolderMessage(folder_name, SubfolderAction.Add).construct_message_json().encode())
            subfolder_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            subfolder_message = MessageBasis.parse_from_json(subfolder_resp)
            if subfolder_message is not None and isinstance(subfolder_message, AckMessage):
                if subfolder_message.code() == 200:
                    self.after(0, lambda: messagebox.showinfo("Success", "Subfolder created successfully."))
                    self.after(0, self.request_files)
                else:
                    self.after(0, lambda: messagebox.showinfo("Failure", f"Failed to create subfolder because: {subfolder_message.message()}"))
            self.after(0, self.update_button_states)
        except Exception as e:
            print(f"Error: {e}")

    # thread for deleting subfolder
    def delete_subfolder(self):
        selected_dir = self.file_list.get(self.file_list.curselection())
        selected_dir = selected_dir.split(" ")[0].strip()
        
        if selected_dir is not None or len(selected_dir) > 0:
            threading.Thread(target=self._delete_subfolder(selected_dir)).start()
            
    # deletes subfolder from server
    def _delete_subfolder(self, selected_dir):
        try:
            self.master.con.sendall(SubfolderMessage(selected_dir, SubfolderAction.Delete).construct_message_json().encode())
            subfolder_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            subfolder_message = MessageBasis.parse_from_json(subfolder_resp)
            if subfolder_message is not None and isinstance(subfolder_message, AckMessage):
                if subfolder_message.code() == 200:
                    self.after(0, lambda: messagebox.showinfo("Success", "Subfolder deleted successfully."))
                    self.after(0, self.request_files)
                else:
                    self.after(0, lambda: messagebox.showinfo("Failure", f"Failed to delete subfolder because: {subfolder_message.message()}"))
            self.after(0, self.update_button_states)
        except Exception as e:
            print(f"Error: {e}")
    
    # thread for moving directory
    def move_directory(self, move_path):
        threading.Thread(target=self._move_directory, args=(move_path,)).start()

    # moves directory on server
    def _move_directory(self, move_path):
        try:
            # Send move message to server
            self.master.con.sendall(MoveMessage(move_path).construct_message_json().encode())
            
            # Get server response
            move_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            move_message = MessageBasis.parse_from_json(move_resp)
            
            if move_message and isinstance(move_message, AckMessage):
                if move_message.code() == 200:
                    # Only update UI after successful server response
                    self.request_files()  # This will update file list and current_dir
                else:
                    self.show_error(f"Failed to move to directory: {move_message.message()}")
                        
        except Exception as e:
            self.show_error(f"Error during directory navigation: {e}")
    
    # moving to different directory
    def move_up_directory(self):
        try:
            # Send move message with ".." to go up one level
            self.master.con.sendall(MoveMessage("..").construct_message_json().encode())
            
            move_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            move_message = MessageBasis.parse_from_json(move_resp)
            
            if move_message is not None and isinstance(move_message, AckMessage):
                if move_message.code() == 200:
                    self.request_files()  # Update file list and current_dir
                else:
                    self.show_error(f"Failed to move up: {move_message.message()}")
                    
        except Exception as e:
            self.show_error(f"Error moving up directory: {e}")
    
    # updates button states
    def update_button_states(self):
        selected_indices = self.file_list.curselection()
        if not selected_indices:
            self.download_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.open_folder_button.config(state=tk.DISABLED)
            return

        selected_index = selected_indices[0]
        selected_item = self.file_list.get(selected_index)
        if selected_item.endswith(" (f)"):
            self.download_button.config(state=tk.NORMAL)
            self.delete_button.config(state=tk.NORMAL)
            self.open_folder_button.config(state=tk.DISABLED)
        elif selected_item.endswith(" (d)"):
            self.download_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.open_folder_button.config(state=tk.NORMAL)
        else:
            # In case the format is unexpected
            self.download_button.config(state=tk.DISABLED)
            self.delete_button.config(state=tk.DISABLED)
            self.open_folder_button.config(state=tk.DISABLED)

    # on file select, update button states
    def on_file_select(self, event):
        self.update_button_states()

    # clears socket buffer so client can continue
    def clear_socket_buffer(self):
        try:
            self.master.con.settimeout(0.1)
            while True:
                data = self.master.con.recv(1024)
                if not data:
                    break
        except Exception as e:
            pass
        finally:
            self.master.con.settimeout(None)
    
    # displays errors
    def show_error(self, message):
        self.after(0, lambda: messagebox.showerror("Error", message))

class PerformancePage(Page):
    """
    Displays performance metrics like data transfer rates and latency.
    Shows real-time statistics about file operations.
    """
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)
        self.data_rate = None
        self.file_transfer_time = None
        self.latency = None

    # create content
    def create_content(self):
        self.master.create_topbar("Performance")

        self.performance_label = tk.Label(
            self,
            text="Performance Metrics",
            font=("Figtree", 24),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.performance_label.pack(pady=10)

        # self.performance_text = tk.Text(
        #     self,
        #     height=20,
        #     width=80,
        #     font=("Figtree", 12),
        #     fg=self.text_color,
        #     bg=self.bg_color
        # )
        # self.performance_text.pack(pady=10)
        
        self.data_rate_label = tk.Label(
            self,
            text=f"Data Rate (MB/s): {self.data_rate}",
            font=("Figtree", 14),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.data_rate_label.pack(pady=10)
        
        self.file_transfer_label = tk.Label(
            self,
            text=f"File Transfer Time (s): {self.file_transfer_time}",
            font=("Figtree", 14),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.file_transfer_label.pack(pady=10)
        
        self.latency_label = tk.Label(
            self,
            text=f"Latency (s): {self.latency}",
            font=("Figtree", 14),
            fg=self.text_color,
            bg=self.bg_color
        )
        self.latency_label.pack(pady=10)

        self.get_stats()

    # updates labels
    def update_labels(self):
        data_rate_rounded = round(self.data_rate, 2) if self.data_rate is not None else 0
        file_transfer_rounded = round(self.file_transfer_time, 2) if self.file_transfer_time is not None else 0
        latency_rounded = round(self.latency, 2) if self.latency is not None else 0

        self.data_rate_label.config(text=f"Data Rate (MB/s): {data_rate_rounded}")
        self.file_transfer_label.config(text=f"File Transfer Time (s): {file_transfer_rounded}")
        self.latency_label.config(text=f"Latency (s): {latency_rounded}")

    # gets stats from server on recent upload or download
    def get_stats(self):
        try:
            
            self.master.con.sendall(StatsMessage().construct_message_json().encode())
            stats_resp = self.master.con.recv(1024).strip(b'\x00').decode("utf-8")
            stats_message = MessageBasis.parse_from_json(stats_resp)
            if stats_message is not None and isinstance(stats_message, StatsMessage):
                self.data_rate = stats_message.data_rates()
                self.file_transfer_time = stats_message.file_transfer_time()
                self.latency = stats_message.latency()
                self.update_labels()
            else:
                self.show_error(f"Failed to get performance stats: {stats_message.message()}")
        except Exception as e:
            self.show_error(f"Error: {e}")

    # refreshes stats
    def refresh_stats(self):
        self.get_stats()

    # shows error
    def show_error(self, message):
        self.after(0, lambda: messagebox.showerror("Error", message))

class SettingsPage(Page):
    """
    Handles application theme customization.
    Allows users to modify colors and save preferences.
    """
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)
        self.current_colors = {
            "bg_color": bg_color,
            "text_color": text_color,
            "button_color": button_color
        }
        self.reset_content()

    # creates content
    def create_content(self):
        title = tk.Label(
            self,
            text="Settings",
            font=("Figtree", 24, "bold"),
            bg= self.current_colors["bg_color"],
            fg=self.current_colors["text_color"]
        )
        title.pack(pady=10)
        
        for color_key in self.current_colors:
            frame = tk.Frame(self, bg=self.current_colors["bg_color"])
            frame.pack(pady=10)

            label = tk.Label(
                frame,
                text=f"{color_key.title()} Color:",
                bg=self.current_colors["bg_color"],
                fg=self.current_colors["text_color"]
            )
            label.pack(side=tk.LEFT, padx=10)

            preview = tk.Label(
                frame,
                width=10,
                bg=self.current_colors[color_key]
            )
            preview.pack(side=tk.LEFT, padx=5)

            btn = tk.Button(
                frame,
                text="Choose",
                command=lambda k=color_key, p=preview: self.pick_color(k, p),
                bg=self.current_colors["button_color"]
            )
            btn.pack(side=tk.LEFT, padx=5)

        # Apply button
        apply_btn = tk.Button(
            self,
            text="Apply Changes",
            command=self.apply_colors,
            bg=self.current_colors["button_color"]
        )
        apply_btn.pack(pady=20)

        # Reset button
        reset_btn = tk.Button(
            self,
            text="Reset to Defaults",
            command=self.reset_colors,
            bg=self.current_colors["button_color"]
        )
        reset_btn.pack(pady=5)

    # allows user to select color
    def pick_color(self, color_key, preview):
        color = colorchooser.askcolor(color=self.current_colors[color_key])[1]
        if color:
            self.current_colors[color_key] = color
            preview.configure(bg=color)
    
    # applies colors
    def apply_colors(self):
        self.master.update_theme(
            self.current_colors["bg_color"],
            self.current_colors["text_color"],
            self.current_colors["button_color"]
    )

    # updates page colors
    def _update_page_colors(self):
        for widget in self.winfo_children():
            if isinstance(widget, tk.Label):
                widget.configure(
                    bg=self.current_colors["bg_color"],
                    fg=self.current_colors["text_color"]
                )
            elif isinstance(widget, tk.Button):
                widget.configure(bg=self.current_colors["bg_color"])
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=self.current_colors["bg_color"])

    # resets colors to default
    def reset_colors(self):
        self.current_colors = {
            "bg_color": "#2C2C2C",
            "text_color": "white",
            "button_color": "#BB86FC"
        }
        self.apply_colors()

class ConnectPage(Page):    
    """
    Handles user authentication and server connection.
    Manages login credentials and connection settings.
    """
    def __init__(self, parent, bg_color, text_color, button_color):
        super().__init__(parent, bg_color, text_color, button_color)
        self.username = ""
        self.password = ""
        self.ip = "127.0.0.1"
        self.port = 61324
        self.create_content()

    # hashes password with sha256
    def hash_password(self, plain_password):
        hashed_password = hashlib.sha256(plain_password.encode()).hexdigest()
        return hashed_password
    
    # thread to start login validation
    def validate_login(self):
        threading.Thread(target=self._validate_login).start()

    # validates login credentials with server
    def _validate_login(self):
        self.username = self.username_entry.get()
        self.password = self.password_entry.get()
        self.create_connection()
        hashed_password = self.hash_password(self.password)

        connect_message = ConnectMessage(username=self.username, passwordHash=hashed_password)
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
            
            MessageBasis.parse_from_json(contents.decode("utf-8"))
            if message.code() == 200:
                self.master.show_page("My Files")
                self.master.enable_buttons()
            elif message.code() == 401:
                messagebox.showerror("Error", "Invalid credentials.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")

    # saves connection details, with ip and port
    def save_connection_details(self):
        try:
            ip = self.ip_address_entry.get()
            port = self.port_entry.get()

            if ip:
                self.ip = ip
            if port:
                self.port = int(port)
            
            messagebox.showinfo("Info", "Connection details saved.")
        except ValueError:
            messagebox.showerror("Error", "Invalid port number.")

    # creates connection with server
    def create_connection(self):
        try:
            self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.con.connect((self.ip, self.port))
            self.master.con = self.con
            self.master.status_update("Online")
        except Exception as e:
            print(f"Error: {e}")
            if self.con:
                self.con.close()
            self.master.status_update("Offline")

    # creates content
    def create_content(self):
        self.reset_content()

        user_pass_frame = tk.Frame(self, bg=self.bg_color)
        user_pass_frame.pack(pady=10)

        label = tk.Label(user_pass_frame, text="Please Login:", font=("Figtree", 24), fg=self.text_color, bg=self.bg_color)
        label.grid(row=0, column=0, columnspan=2, pady=20)

        self.username_label = tk.Label(user_pass_frame, text="Username:", font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.username_label.grid(row=1, column=0, pady=10, sticky="w")

        self.username_entry = tk.Entry(user_pass_frame, font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.username_entry.grid(row=2, column=0, pady=10, padx=10, sticky="ew")

        self.password_label = tk.Label(user_pass_frame, text="Password:", font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.password_label.grid(row=3, column=0, pady=10, sticky="w")

        self.password_entry = tk.Entry(user_pass_frame, font=("Figtree", 14), fg=self.text_color, bg=self.bg_color, show="*")
        self.password_entry.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        ip_port_frame = tk.Frame(self, bg=self.bg_color)
        ip_port_frame.pack(pady=10)

        self.ip_address_label = tk.Label(ip_port_frame, text="Ip-Address:", font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.ip_address_label.grid(row=0, column=0, pady=10, sticky="w")

        self.ip_address_entry = tk.Entry(ip_port_frame, font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.ip_address_entry.grid(row=1, column=0, pady=10, padx=10, sticky="ew")

        self.port_label = tk.Label(ip_port_frame, text="Port:", font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.port_label.grid(row=0, column=1, pady=10, sticky="w")
        
        self.port_entry = tk.Entry(ip_port_frame, font=("Figtree", 14), fg=self.text_color, bg=self.bg_color)
        self.port_entry.grid(row=1, column=1, pady=10, padx=10, sticky="ew")

        button_frame = tk.Frame(self, bg=self.bg_color)
        button_frame.pack(pady=10)

        self.login_button = Button(button_frame, text="Login", font=("Figtree", 14), bg=self.button_color, fg=self.text_color, command=self.validate_login, borderless=1)
        self.login_button.pack(side=tk.LEFT, pady=10)

        self.save_button = Button(button_frame, text="Save", font=("Figtree", 14), bg=self.button_color, fg=self.text_color, command=self.save_connection_details, borderless=1)
        self.save_button.pack(side=tk.RIGHT, pady=10)

        # Configure grid columns to expand
        user_pass_frame.grid_columnconfigure(0, weight=1)
        ip_port_frame.grid_columnconfigure(0, weight=1)
        ip_port_frame.grid_columnconfigure(1, weight=1)