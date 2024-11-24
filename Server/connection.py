import threading
import socket
import time

from .credentials import Credentials, user_database
from .io_tools import root_directory, move_relative, create_directory_info, make_relative, get_file_type, is_path_valid
from .network_analysis import network_analyzer
from .server_io import RequestUpload, UploadFile, ExtractFileContents, DeleteFile, ModifySubdirectories
from Common.message_handler import *
from Common.file_io import split_binary_for_network
from Common.http_codes import HttpCodes, HTTPErrorBasis

class ConnectionCore:
    def __init__(self, conn: socket.socket, addr, path: Path):
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
    def conn(self) -> socket.socket | None:
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

    def setup(self, conn: socket.socket, addr):
        global root_directory

        if self.is_connected():
            self.kill()

        self.__core = ConnectionCore(conn, addr, root_directory)
        self.__core.conn().settimeout(3.0)
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
        self.__thread.start()
    def join(self):
        if self.__thread != None and self.__thread.is_alive():
            self.__thread.join()
    def kill(self):
        if self.__core != None and self.__thread != None:
            self.__core.drop()
            self.join()

            self.__thread = None
            self.__core = None

def recv_message(connection: socket.socket, buff_size: int) -> MessageBasis | None:
    try:
        contents = connection.recv(buff_size)

        if contents is None or len(contents) == 0:
            return None # Connection closed
    except socket.timeout as e:
        raise e
    except Exception as e: # Unexpected error
        raise e
    
    result = MessageBasis.parse_from_json(contents)
    if result is None:
        raise ValueError("Invalid format")
    else:
        return result
def send_message(connection: socket.socket, message: MessageBasis, response: bool = True):
    connection.sendall(message.construct_message_json(request=not response).encode())

def connection_proc(conn: ConnectionCore) -> None:
    global user_database
    global network_analyzer

    addr_str = conn.addr()[0]
    print(f"[{addr_str}] Started connection proc")
    
    conn.conn().settimeout(3.0)
    print(f"[{addr_str}] Awaiting Connect message...")

    conn_msg = None
    while conn_msg is None:
        try:
            if not conn.lock():
                print("f[{addr_str}] Closing connection")

            conn_msg = recv_message(conn.conn(), 1024)
            if conn_msg is None: # Conn terminated
                print(f"[{addr_str}] Connection terminated.")
                conn.unlock()
                conn.drop()
                return
            if not isinstance(conn_msg, ConnectMessage):
                print(f"[{addr_str}] Expected ConnectMessage, got '{conn_msg.message_type().value}'. Trying again.")
                continue

        except socket.timeout:
            continue # Blocking control
        except ValueError:
            print(f"[{addr_str}] Invalid message format. Expected ConnectionMessage")
        except Exception as e:
            print(f"[{addr_str}] Caught unexpected error '{str(e)}'. Terminating")
            conn.unlock()
            conn.drop()

            return 
        finally:
            conn.unlock()
    
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

    if not conn.lock():
        print("f[{addr_str}] Closing connection")
    send_message(conn.conn(), connect_ack)

    conn.unlock()
    if not keep_connection:
        print(f"[{addr_str}] Authentication failed for user. Closing connection")
        conn.drop()
        return
    else:
        print(f"[{addr_str}] Authentication success.")
        conn.set_cred(target_cred)

    buff_size = 1024

    try:
        while True:
            # This is our message loop. It will accept messages, process them, and then perform the actions needed.
            
            message = None
            while message is None:
                try:
                    if not conn.lock():
                        print(f"[{addr_str}] Could not obtain lock, closing connection")
                        conn.unlock()
                        conn.drop()
                        return

                    message = recv_message(conn.conn(), 1024)
                    if message is None: # Conn terminated
                        print(f"[{addr_str}] Connection terminated.")
                        conn.unlock()
                        conn.drop()
                        return

                except socket.timeout:
                    continue # Blocking control
                except ValueError:
                    print(f"[{addr_str}] Invalid message format.")
                except Exception as e:
                    print(f"[{addr_str}] Caught unexpected error '{str(e)}'. Terminating")
                    conn.unlock()
                    conn.drop()
                finally:
                    conn.unlock()
            
            print(f"[{addr_str}] Processing request of kind {message.message_type().value}")

            if not conn.lock(): # We need our socket
                print(f"[{addr_str}] Closing connection")

            responses = []
            match message.message_type():
                case MessageType.Connect:
                    # Invalid, already connected
                    responses.append(AckMessage(418, "Already connected"))

                case MessageType.Close:
                    responses.append(AckMessage(200, "Goodbye!"))

                case MessageType.Ack:
                    print(f"[{addr_str}] Got ack with code {message.code()}, message '{message.message()}'")

                case MessageType.Upload:
                    path, kind, size = message.name(), message.kind(), message.size()

                    conn.conn().settimeout(None)

                    path = move_relative(path, conn.path())
                    upload_handle = RequestUpload(path, size, conn.cred())
                    if isinstance(upload_handle, HTTPErrorBasis):
                        responses.append(upload_handle.to_ack())
                        upload_handle = None
                    else:
                        start_time = time.perf_counter()

                        send_message(conn.conn(), AckMessage(200, "OK"))
                        print(f"[{addr_str}] Processing upload of frame size {size}")

                        # Now we get our file
                        if UploadFile(upload_handle, conn.conn(), size):
                            responses.append(AckMessage(200, "OK"))
                            print(f"[{addr_str}] Upload success")
                        else:
                            responses.append(AckMessage(HttpCodes.Conflict, "File upload failed"))
                            print(f"[{addr_str}] Upload failed")

                        end_time = time.perf_counter()
                        network_analyzer.record_transfer(size * 4096, start_time, end_time, addr_str)

                    conn.conn().settimeout(3.0)

                case MessageType.Download:
                    path = message.path()
                    path = move_relative(path, conn.path())

                    file_contents = ExtractFileContents(path, conn.cred())
                    if isinstance(file_contents, HTTPErrorBasis):
                        responses.append(DownloadMessage(file_contents.code, file_contents.message, None, None))
                        
                    else:
                        kind = get_file_type(path)
                        size = len(file_contents)

                        start_time = time.perf_counter()

                        send_message(conn.conn(), DownloadMessage(HttpCodes.Ok, "OK", kind, size))
                        
                        try:
                            ack = recv_message(conn.conn(), buff_size)
                            if ack is None or not isinstance(ack, AckMessage):
                                print(f"[{addr_str}] Message recieved, expected ack, but got {ack.message_type().value if ack is not None else None}")
                            
                            if ack.code() == 200:
                                for item in file_contents:
                                    conn.conn().sendall(item)
                            else:
                                print(f'[{addr_str}] Could not download because of {ack.message()}')

                            ack = recv_message(conn.conn(), buff_size)
                            if ack is None or not isinstance(ack, AckMessage):
                                print(f"[{addr_str}] Message recieved, expected ack, but got {ack.message_type().value if ack is not None else None}")

                            
                            if ack.code() == 200:
                                print(f'[{addr_str}] Download completed')
                            else:
                                print(f'[{addr_str}] Could not download because of {ack.message()}. Stats are still recorded')

                            end_time = time.perf_counter()
                            network_analyzer.record_transfer(size * 4096, start_time, end_time, addr_str)
                            
                        except Exception as e:
                            responses.append(AckMessage(HttpCodes.Conflict, str(e)))

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
                        # Use current path for directory listing
                        dir_structure = create_directory_info(conn.path())
                        dir_contents = json.dumps(dir_structure.to_dict()).encode()
                        network_dir = split_binary_for_network(dir_contents)

                        curr_dir = make_relative(conn.path())

                        send_message(conn.conn(), DirMessage(200, "OK", curr_dir, len(network_dir)))
                        ack = recv_message(conn.conn(), buff_size)
                        if ack is None or not isinstance(ack, AckMessage):
                            print(f"[{addr_str}] Invalid ack received for dir message")
                            continue

                        if ack.code() != HttpCodes.Ok.value:
                            print(f"[{addr_str}] Dir failed, client responded with '{ack.message()}'")

                        for item in network_dir:
                            conn.conn().sendall(item)
                        
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
                case MessageType.Stats:
                    last = network_analyzer.get_last_ip_stats(addr_str)
                    responses.append(
                        StatsMessage(last.data_rate, last.transfer_time, last.latency) if last is not None else StatsMessage(0, 0, 0)
                    )
                    
            print(f"[{addr_str}] Response contains {len(responses)} message(s)")
            if responses is not None and len(responses) != 0:
                for response in responses:
                    if isinstance(response, MessageBasis):
                        send_message(conn.conn(), response)
                    elif isinstance(response, str):
                        conn.conn().send(response.encode())
                    else:
                        conn.conn().send(response) # Binary

            conn.unlock()

    except OSError as e:
        print(f"OSError caught: {str(e)}\nClosing connection")
        conn.unlock()
        conn.drop()
        return
    finally:
        conn.unlock()