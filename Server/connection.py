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
        
        message = MessageBasis.parse_from_json(contents)
        if message is None:
            print(f"[{conn.addr()}] Invalid format, the connection message was invalid or not received")
            conn.unlock()
            conn.drop()
            return

        response = None
        match message.message_type():
            case MessageType.Connect:
                # Invalid, already connected
                response = AckMessage(418, "Already connected")

            case MessageType.Close:
                response = AckMessage(200, "Goodbye!")

            case MessageType.Ack:
                response = AckMessage(418, "Server cannot receive an ack")

            case MessageType.Size:
                if last_was == MessageType.Size:
                    buff_size =
            case MessageType.Upload:
                pass
            case MessageType.Download:
                pass
            case MessageType.Delete:
                pass
            case MessageType.Dir:
                # Get directory info from backend
                try:
                    info = DirectoryInfo("") # Dummy
                    response = DirMessage(200, "OK", info, conn.path())

                except: # Not signed in 
                    response = DirMessage(401, "Not signed in", None, None)
            
            case MessageType.Move:
                pass
            case MessageType.Subfolder:
                pass

        if response is not None:
            response_str = response.construct_message_json()
            conn.conn().send(response_str.encode())

        if last_was == MessageType.Size:
            buff_size = buff_size_prev 
            
        last_was = message.message_type()

        conn.unlock()