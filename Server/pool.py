import threading
from credentials import *
from socket import socket as soc
import socket 
import json

class ConnectionCore:
    def __init__(self, conn: soc, addr):
        self.__conn = conn
        self.__addr = addr
        self.__lock = threading.Lock()
        self.__cred = None

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
        self.__conn = None
        self.__addr = None
        self.__cred = None
        self.unlock()

    def addr(self):
        return self.__addr
    def conn(self) -> soc:
        return self.__conn
    def cred(self) -> Credentials:
        return self.__cred

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
    print("\tStarted connection proc")
    if not conn.lock():
        return
    
    print("\tSending message")
    conn.conn().send("Hello my friend".encode())

    print("\t sent")
    conn.unlock()
    

class ThreadPool:
    def __init__(self):
        self.__socket = soc(socket.AF_INET, socket.SOCK_STREAM)
        self.__bound = False
        self.__cons = [Connection() for x in range(4)]

    def bind(self, port: int, address: str = None):
        self.__socket.bind((address, port))
        self.__bound = True

    def listen(self):
        if not self.__bound:
            raise Exception("Could not start listening if the port is not bound")

        self.__socket.listen()

    def kill(self):
        for conn in self.__cons:
            conn.kill()
        self.__cons.clear()
        self.__cons = None
        self.__socket.close()
        self.__socket = None
        self.__bound = False

    def __get_next_open(self) -> Connection:
        if not self.__bound:
            return None
        
        for con in self.__cons:
            if not con.is_connected():
                return con
            
        # at this point, there are no open ones, so we add one.
        newConn = Connection()
        self.__cons.append(newConn)
        return newConn
    
    def mainLoop(self):
        while True:
            c, addr = self.__socket.accept()
            print(f"Accepted connection from ${addr}")

            open_conn = self.__get_next_open()
            if open_conn == None:
                raise Exception("An open connection could not be obtained")
            open_conn.setup(c, addr)
            open_conn.start()