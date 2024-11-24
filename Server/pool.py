from .credentials import *
from socket import socket as soc
import socket 

from .connection import Connection

class ThreadPool:
    def __init__(self):
        self.__socket = soc(socket.AF_INET, socket.SOCK_STREAM)
        self.__bound = False
        self.__cons = [Connection() for x in range(4)]

    def bind(self, port: int, address: str = None):
        self.__socket.bind((address, port))
        self.__socket.settimeout(4.0)
        self.__bound = True

    def listen(self):
        if not self.__bound:
            raise Exception("Could not start listening if the port is not bound")

        self.__socket.listen()

    def kill(self):
        self.__socket.close()
        
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
        print("[CONTROL] Entering main loop, accepting connections")
        while True:
            try:
                c, addr = self.__socket.accept()

                open_conn = self.__get_next_open()
                if open_conn == None:
                    print("[CONTROL] Error! Could not get worker thread for connection. Closing connection")
                    c.close()
                else:
                    print(f"[CONTROL] Accepted connection from {addr[0]} on port {addr[1]}")
                    open_conn.setup(c, addr)
                    open_conn.start()
            except socket.timeout:  
                continue