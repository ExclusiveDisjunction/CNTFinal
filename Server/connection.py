import threading
from credentials import *
from socket import socket as soc
from ..Common.message_handler import *

class ConnectionCore:
    def __init__(self, conn: soc, addr, path: str | None):
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
        if self.__lock != None:
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
        if self.is_connected():
            self.kill()

        self.__core = ConnectionCore(conn, addr)
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

def connection_proc(conn: ConnectionCore) -> None:
    print(f"[{conn.addr()}] Started connection proc")
    if not conn.lock():
        return
    
    print("[*] Awaiting Connect message...")
    contents = conn.conn().recv(1024)
    if contents == "" or contents is None:
        print(f"[{conn.addr()}] Connection terminated")
        conn.unlock()
        conn.drop()
        return

    conn_msg = MessageBasis.parse_from_json(contents)
    if conn_msg is None or not isinstance(conn_msg, ConnectMessage):
        print(f"[{conn.addr()}] Invalid format, the connection message was invalid or not received")
        conn.unlock()
        conn.drop()
        return
    
    conn.set_cred( Credentials(conn_msg.username(), conn_msg.passwordHash()) )
    conn.unlock()

    last_was = None
    last_was_ok = True
    buff_size = 1024
    buff_size_prev = None
    while conn.lock():
        # This is our message loop. It will accept messages, process them, and then perform the actions needed.

        contents = conn.conn().recv(buff_size)
        if contents == "" or contents is None:
            print(f"[{conn.addr()}] Connection terminated")
            conn.unlock()
            conn.drop()
            return
        
        # We need to treat this as a file, not a message
        if last_was_ok and last_was == MessageType.Upload:
            # Pass the file to the IO model
            pass
        
        message = MessageBasis.parse_from_json(contents)
        if message is None:
            print(f"[{conn.addr()}] Invalid format, the connection message was invalid or not received")
            conn.unlock()
            conn.drop()
            return
        

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
                if last_was != MessageType.Size:
                    buff_size_prev = buff_size

                buff_size = message.size()
                # Size has no response 

            case MessageType.Upload:
                name, kind, size = message.name(), message.kind(), message.size()
                # Pass to the IO model
                can_send = True # Dummy value
                error_value = (401, "Unauthorized") # Dummy value

                if can_send:
                    responses.append(AckMessage(100, "Send file"))
                else:
                    responses.append(AckMessage(error_value[0], error_value[2]))

            case MessageType.Download:
                path = message.path()
                
                # We need to validate the request with the IO model
                can_send = True
                error = (401, "Unauthorized") # Both dummy values
                file_info = (FileType.Text, 200)
                file = "Dummy file contents"

                if can_send:
                    responses.append(DownloadMessage(200, "OK", file_info[0], file_info[1]))
                    responses.append(file)
                else:
                    responses.append(DownloadMessage(error[0], error[1], None, None))

            case MessageType.Delete:
                path = message.path()

                # Validate request with IO model
                status = (200, "OK")
                responses.append(AckMessage(status[0], status[1]))

            case MessageType.Dir:
                # Get directory info from backend
                try:
                    info = DirectoryInfo("") # Dummy
                    dir_resp = DirMessage(200, "OK", info, conn.path())
                    size = len(dir_resp.construct_message_json())

                    responses.append(SizeMessage(size))
                    responses.append(dir_resp)

                except: # Not signed in 
                    responses.append(DirMessage(401, "Not signed in", None, None))
            
            case MessageType.Move:
                path = message.path()

                # Validate request with IO model
                status = (200, "OK")
                responses.append(AckMessage(status[0], status[1]))    
            
            case MessageType.Subfolder:
                path, action = message.path(), message.action()

                # Validate request with IO model
                status = (200, "OK")
                responses.append(AckMessage(status[0], status[1]))
                

        if responses is not None and len(responses) != 0:
            for response in responses:
                if isinstance(response, MessageBasis):
                    response_str = response.construct_message_json()
                    conn.conn().send(response_str.encode())
                elif isinstance(response, str):
                    conn.conn().send(response.encode())

        if last_was == MessageType.Size:
            buff_size = buff_size_prev 

        last_was = message.message_type()

        conn.unlock()