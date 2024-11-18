import threading
from socket import socket as soc

from .credentials import *
from .io_tools import root_directory, move_relative, create_directory_info, make_relative, get_file_type
from .file_io import *
from Common.message_handler import *

class ConnectionCore:
    def __init__(self, conn: soc, addr, path: Path):
        if path is None:
            raise ValueError("Path cannot be None")

        self.__conn = conn
        self.__addr = addr
        self.__lock = threading.Lock()
        self.__cred = None
        self.__path = path

    def set_cred(self, cred: Credentials) -> None:
        self.__cred = cred

    def has_cred(self) -> bool:
        return self.__cred != None
    def empty(self) -> bool:
        return self.__conn == None and self.__addr == None

    def lock(self) -> bool:
        if self.empty():
            return False
        else:
            self.__lock.acquire()
            return True
    def unlock(self):
        if self.__lock != None and self.__lock.locked():
            self.__lock.release()
    def drop(self):
        self.lock()
        if self.__conn is not None:
            self.__conn.close()

        self.__conn = None
        self.__addr = None
        self.__cred = None
        self.unlock()

    def addr(self):
        return self.__addr
    def conn(self) -> soc | None:
        return self.__conn
    def cred(self) -> Credentials | None:
        return self.__cred
    def set_cred(self, new_cred: Credentials | None):
        self.__cred = new_cred
    def path(self) -> str | None:
        return self.__path
    def set_path(self, new_path: str | None):
        self.__path = new_path

class Connection:
    def __init__(self): 
        self.__core = None
        self.__thread = None

    def setup(self, conn: soc, addr):
        global root_directory

        if self.is_connected():
            self.kill()

        self.__core = ConnectionCore(conn, addr, root_directory)
        self.__thread = threading.Thread(target=connection_proc, args=[self.__core])

    def is_connected(self):
        if self.__thread == None:
            return False
        else:
            if not self.__thread.is_alive():
                self.__thread = None
                self.__core = None
                return False
            else:
                return True

    def start(self):
        if self.__thread == None or self.__thread.is_alive():
            raise RuntimeError("Could not start this thread knowing that the thread is non-existent or is already running")
        self.__thread.run()
    def join(self):
        if self.__thread != None and self.__thread.is_alive():
            self.__thread.join()
    def kill(self):
        if self.__core != None and self.__thread != None:
            self.__core.drop()
            self.join()

            self.__thread = None
            self.__core = None

def recv_message(connection: soc, buff_size: int) -> MessageBasis | None:
    contents = connection.recv(buff_size)
    if contents is None or len(contents) == 0:
        return False
    
    result = MessageBasis.parse_from_json(contents)
    if result is None:
        return None
    else:
        return result

def connection_proc(conn: ConnectionCore) -> None:
    global user_database

    addr_str = conn.addr()[0]
    print(f"[{addr_str}] Started connection proc")
    if not conn.lock():
        return
    
    print(f"[{addr_str}] Awaiting Connect message...")

    conn_msg = recv_message(conn.conn(), 1024)
    if conn_msg is None or not isinstance(conn_msg, ConnectMessage):
        print(f"[{addr_str}] Connection dropped or message is of invalid format")
        conn.unlock()
        conn.drop()
        return
    
    target_cred = Credentials(conn_msg.username(), conn_msg.passwordHash())
    user_lookup = user_database.get_user(target_cred.getUsername())
    keep_connection = True
    connect_ack = None
    if user_lookup is None:
        user_database.set_user_pass(target_cred)
        connect_ack = AckMessage(HttpCodes.Ok, f"Welcome new user, '{target_cred.getUsername()}'")
    else:
        if target_cred.getPasswordHash() != user_lookup.getPasswordHash():
            connect_ack = AckMessage(HttpCodes.Unauthorized, "Invalid password") # Close down credentials
            keep_connection = False
        else:
            connect_ack = AckMessage(HttpCodes.Ok, f"Welcome back, '{target_cred.getUsername()}'")

    conn.conn().send(connect_ack.construct_message_json().encode())
    if not keep_connection:
        print(f"[{addr_str}] Authentication failed for user. Closing connection")
        conn.unlock()
        conn.drop()
        return
    else:
        print(f"[{addr_str}] Authentication success.")
        conn.set_cred(target_cred)
        conn.unlock()

    buff_size = 1024
    buff_size_prev = None
    size_was_set = None
    cyc_count = 0

    upload_handle = None

    try:
        while conn.lock():
            # This is our message loop. It will accept messages, process them, and then perform the actions needed.

            try:
                contents = conn.conn().recv(buff_size)
            except OSError:
                print(f"[{addr_str}] Connection terminated")
                conn.unlock()
                conn.drop()
                return
            
            if len(contents) == 0 or contents is None:
                print(f"[{addr_str}] Connection terminated")
                conn.unlock()
                conn.drop()
                return
            
            contents = contents.decode()
            
            # We need to treat this as a file, not a message
            if upload_handle is not None and isinstance(upload_handle, UploadHandle):
                result = UploadFile(upload_handle, contents)
                upload_handle = None

                if result:
                    response = AckMessage(200, "OK")
                else:
                    response = AckMessage(HttpCodes.Conflict, "Unable to upload file")

                conn.conn().sendall(response.construct_message_json().encode())
                conn.unlock()
                upload_handle = None
                buff_size = buff_size_prev
                buff_size_prev = None
                size_was_set = None
                continue
            
            try:
                message = MessageBasis.parse_from_json(contents)
            except:
                message = None
            finally:
                if message is None:
                    print(f"[{addr_str}] Invalid format, the connection message was invalid or not received")
                    conn.unlock()
                    conn.drop()
                    return
            
            print(f"[{addr_str}] Processing request of kind {message.message_type()}")

            responses = []
            match message.message_type():
                case MessageType.Connect:
                    # Invalid, already connected
                    responses.append(AckMessage(418, "Already connected"))

                case MessageType.Close:
                    responses.append(AckMessage(200, "Goodbye!"))

                case MessageType.Ack:
                    responses.append(AckMessage(418, "Server cannot receive an ack"))

                case MessageType.Size:
                    if size_was_set is None or size_was_set >= cyc_count: # Happened in the past
                        buff_size_prev = buff_size

                    buff_size = message.size()
                    size_was_set = cyc_count
                    # Size has no response 

                case MessageType.Upload:
                    path, kind, size = message.name(), message.kind(), message.size()

                    path = move_relative(path, conn.path())
                    upload_handle = RequestUpload(path, size, conn.cred())
                    if isinstance(upload_handle, HTTPErrorBasis):
                        responses.append(upload_handle.to_ack())
                        upload_handle = None
                    else:
                        responses.append(AckMessage(200, "OK"))
                        
                        if size_was_set is None or size_was_set >= cyc_count: # Happened in the past
                            buff_size_prev = buff_size

                        buff_size = size
                        size_was_set = cyc_count

                case MessageType.Download:
                    path = message.path()
                    path = move_relative(path, conn.path())

                    file_contents = ExtractFileContents(path, conn.cred())
                    if isinstance(file_contents, HTTPErrorBasis):
                        responses.append(DownloadMessage(file_contents.code, file_contents.message, None, None))
                        
                    else:
                        kind = get_file_type(path)
                        size = len(file_contents)

                        responses.append(DownloadMessage(HttpCodes.Ok, "OK", kind, size))
                        responses.append(file_contents)

                case MessageType.Delete:
                    path = message.path()
                    path = move_relative(path, conn.path())

                    result = DeleteFile(path, conn.cred())
                    if result is None:
                        responses.append(AckMessage(HttpCodes.Ok, "OK"))
                    else:
                        responses.append(result.to_ack())

                case MessageType.Dir:
                    if conn.cred() is None:
                        responses.append(DirMessage(401, "Not signed in", None, None))
                    else:
                        dir_structure = create_directory_info()
                        curr_dir = make_relative(conn.path())
                        dir_as_str = DirMessage(200, "OK", curr_dir, dir_structure).construct_message_json(request=False)

                        size = len(dir_as_str)
                        responses.append(SizeMessage(size))
                        responses.append(dir_as_str)
                        
                case MessageType.Move:
                    path = message.path()
                    path = move_relative(path, conn.path())

                    if not is_path_valid(path):
                        responses.append(AckMessage(HttpCodes.Forbidden, "Invalid path"))
                    else:
                        conn.set_path(path)
                        responses.append(AckMessage(HttpCodes.Ok, "OK"))
                
                case MessageType.Subfolder:
                    path, action = message.path(), message.action()
                    path = move_relative(path, conn.path())

                    result = ModifySubdirectories(path, action)
                    if result is None:
                        responses.append(AckMessage(200, "OK"))
                    else:
                        responses.append(result.to_ack())

            print(f"[{addr_str}] Response contains {len(responses)} message(s)")
            if responses is not None and len(responses) != 0:
                for response in responses:
                    if isinstance(response, MessageBasis):
                        response_str = response.construct_message_json(request=False)
                        if isinstance(response, SizeMessage) or (isinstance(response, DownloadMessage) and response.is_response()):
                            conn.conn().send(response_str.encode().ljust(1024, b'\x00'))
                        else:
                            conn.conn().send(response_str.encode())
                    elif isinstance(response, str):
                        conn.conn().send(response.encode())

            if size_was_set is not None and size_was_set < cyc_count and buff_size_prev is not None:
                buff_size = buff_size_prev 
                size_was_set = None
                buff_size_prev = None

            cyc_count += 1
            conn.unlock()
    except OSError as e:
        print(f"OSError caught: {str(e)}\nClosing connection")
        conn.unlock()
        conn.drop()
        return