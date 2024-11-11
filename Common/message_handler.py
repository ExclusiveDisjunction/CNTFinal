import json
from enum import Enum
from typing import Self

from Server.server_path import DirectoryInfo, FileType

class MessageType(Enum):
    Connect = "connect"
    Close = "close"
    Ack = "ack"
    Upload = "upload"
    Download = "download"
    Delete = "delete"
    Dir = "dir"
    Move = "move"
    Subfolder = "subfolder"

class MessageBasis:
    def message_type(self) -> MessageType:
        raise NotImplementedError()
    def data(self) -> dict:
        return {}
    def data_response(self) -> dict:
        return {}
    
    def __eq__(self, other: Self) -> bool:
        try:
            return self.message_type() == other.message_type() and self.data() == other.data() and self.data_response() == other.data_response()
        except:
            return False
    
    def construct_message_json(self, request: bool = True) -> str:
        if request:
            direction_str = "request"
        else:
            direction_str = "response"

        try:
            if request:
                data = self.data()
            else:
                data = self.data_response()
        except:
            raise ValueError("The message does support the current mode")
        
        result = {
            "convention": self.message_type().value,
            "direction": direction_str,
            "data": data
        }

        return json.dumps(result)
    
    def parse_from_json(message: str) -> Self:
        try:
            decoded = json.loads(message)
        except:
            return None

        try:
            msg_type = MessageType(decoded["convention"])

            req_raw = decoded["direction"]
            if req_raw == "request":
                req = True
            elif req_raw == "response":
                req = False
            else:
                req = None

            data = dict(decoded["data"])
        except: 
            msg_type = None
            req = None
            data = None

        if msg_type == None or req == None or data == None:
            return None
        
        try:
            match msg_type:
                case MessageType.Connect:
                    return ConnectMessage.parse(data, req)
                case MessageType.Close:
                    return CloseMessage.parse(data, req)
                case MessageType.Ack:
                    return AckMessage.parse(data, req)
                case MessageType.Upload:
                    return UploadMessage.parse(data, req)
                case MessageType.Download:
                    return DownloadMessage.parse(data, req)
                case MessageType.Delete:
                    return DeleteMessage.parse(data, req)
                case MessageType.Dir:
                    return DirMessage.parse(data, req)
                case MessageType.Move:
                    return MoveMessage.parse(data, req)
                case MessageType.Subfolder:
                    return SubfolderMessage.parse(data, req)
        except:
            return None

class ConnectMessage(MessageBasis):
    def __init__(self, username: str, passwordHash: str):
        self.__username = username
        self.__password = passwordHash

    def message_type(self) -> MessageType:
        return MessageType.Connect
    def data(self) -> dict:
        return {
            "username": self.__username,
            "password": self.__password
        }
    
    def username(self) -> str:
        return self.__username
    def passwordHash(self) -> str:
        return self.__password
    
    def parse(data: dict, req: bool = True) -> Self:
        if not req:
            raise ValueError("Connect message has no response variant")
        
        username = data["username"]
        password = data["password"]
        
        if username == None or password == None:
            raise ValueError("The required fields of username and password were not provided")
        else:
            return ConnectMessage(username, password)

class AckMessage(MessageBasis):
    def __init__(self, code: int, message: str):
        self.__code = code
        self.__message = message

    def message_type(self) -> MessageType:
        return MessageType.Ack
    def data_response(self) -> dict:
        return {
            "code": self.__code,
            "message": self.__message
        }

    def code(self) -> int:
        return self.__code
    def message(self) -> str:
        return self.__message
    
    def parse(data: dict, req: bool = True) -> Self:
        if req:
            raise ValueError("Ack message has no request variant")
        
        try:
            code = int(data["code"])
            message = data["message"]
        except:
            code = None
            message = None
        
        if code == None or message == None:
            raise ValueError("The required fields of username and password were not provided")
        else:
            return AckMessage(code, message)

class CloseMessage(MessageBasis):
    def __init__(self):
        pass 

    def message_type(self) -> MessageType:
        return MessageType.Close
    def data(self) -> dict:
        return { }
    
    def parse(data: dict, req: bool = True) -> Self:
        if not req:
            raise ValueError("Close message has no response variant")

        return CloseMessage()

class UploadMessage(MessageBasis):
    def __init__(self, name: str, kind: FileType, size: int):
        self.__name = name
        self.__kind = kind
        self.__size = size

    def message_type(self) -> MessageType:
        return MessageType.Upload
    def data(self) -> dict:
        return {
            "name": self.__name,
            "kind": self.__kind.value,
            "size": self.__size
        }
    
    def name(self) -> str:
        return self.__name
    def kind(self) -> FileType:
        return self.__kind
    def size(self) -> int:
        return self.__size
    
    def parse(data: dict, req: bool = True) -> Self:
        if not req:
            raise ValueError("Upload message has no response variant")
        
        try:
            name = data["name"]
            kind = FileType(data["kind"])
            size = int(data["size"])
        except:
            name = None
            kind = None
            size = None
        
        if name == None or kind == None or size == None:
            raise ValueError("The dictionary provided does not supply enough information")
        
        return UploadMessage(name, kind, size)

class DownloadMessage(MessageBasis):
    def __init__(self, *args):
        if len(args) == 1:
            self.__path = args[0]
            self.__is_response = False
        elif len(args) == 4:
            status = int(args[0])
            message = args[1]
            kind = args[2]
            size = args[3]

            if (kind == None and size != None) or (kind != None and size == None):
                raise ValueError("The kind and size must both have a value, or neither have a value")

            self.__status = status
            self.__message = message
            self.__is_response = True
            if kind == None and size == None:
                self.__kind = None
                self.__size = None
            else:
                self.__kind = FileType(kind)
                self.__size = int(size)
        else:
            raise ValueError("too many, or not enough, positional arguments supplied")
        

    def message_type(self) -> MessageType:
        return MessageType.Download
    def data(self) -> dict:
        if self.is_response():
            return {}
        
        return {
            "path": self.__path
        }
    def data_response(self) -> dict:
        if self.is_request():
            return {}
        
        if self.__kind == None or self.__size == None: # Format is empty because status is an error code
            format = {

            }
        else:
            format = {
                "kind": self.__kind.value,
                "size": self.__size 
            }

        return {
            "status": self.__status,
            "message": self.__message,
            "format": format
        }
        
    def is_request(self) -> bool:
        return not self.__is_response
    def is_response(self) -> bool:
        return self.__is_response
    
    def path(self) -> str | None:
        if self.is_request():
            return self.__path
        else:
            return None
    def status(self) -> int | None:
        if self.is_response():
            return self.__status
        else:
            return None
    def message(self) -> str | None:
        if self.is_response():
            return self.__message
        else:
            return None
    def kind(self) -> FileType | None:
        if self.is_response():
            return self.__kind
        else:
            return None
    def size(self) -> int | None:
        if self.is_response():
            return self.__size
        else:
            return None
    
    def parse(data: dict, req: bool = True) -> Self:
        if req:
            path = data["path"]

            if path == None:
                raise ValueError("Not enough data to fill this message")
            else:
                return DownloadMessage(path)
        else:
            try:
                status = int(data["status"])
                message = data["message"]
                format = dict(data["format"])
            except:
                status = None
                message = None
                format = None

            if status == None or message == None or format == None:
                raise ValueError("Not enough data to fill this message")
            
            if len(format) == 0:
                return DownloadMessage(status, message, None, None)
            else:
                return DownloadMessage(status, message, format["kind"], format["size"])

class DeleteMessage(MessageBasis):
    def __init__(self, path: str):
        self.__path = path

    def message_type(self) -> MessageType:
        return MessageType.Delete
    def data(self) -> dict:
        return {
            "path": self.__path
        }

    def path(self) -> str:
        return self.__path
    
    def parse(data: dict, req: bool = True) -> Self:
        if not req:
            raise ValueError("Delete message has no response variant")
        
        path = data["path"]

        if path == None:
            raise ValueError("Not enough data supplied")
        else:
            return DeleteMessage(path)

class DirMessage(MessageBasis):
    def __init__(self, *args):
        if len(args) == 0:
            self.__is_response = False
        elif len(args) == 3:
            code = args[0]
            message = args[1]
            root = args[2]

            if not isinstance(root, DirectoryInfo):
                raise ValueError("The root must be a directory info")

            self.__is_response = True
            self.__code = code
            self.__message = message
            self.__root = root

    def message_type(self) -> MessageType:
        return MessageType.Dir
    def data(self) -> dict:
        if self.__is_response:
            return {}
        
        return { }
    def data_response(self) -> dict:
        if not self.__is_response:
            return {}
        
        return {
            "response": self.__code,
            "message": self.__message,
            "root": self.__root.to_dict()
        }
    
    def is_request(self) -> bool:
        return not self.__is_response
    def is_response(self) -> bool:
        return self.__is_response
    
    def code(self) -> int | None:
        if self.is_request():
            return None
        else:
            return self.__code
    def message(self) -> str | None:
        if self.is_request():
            return None
        else:
            return self.__message
    def root(self) -> DirectoryInfo | None:
        if self.is_request():
            return None
        else:
            return self.__root
    
    def parse(data: dict, req: bool = True) -> Self:
        if req:
            return DirMessage()
        else:
            code = None
            message = None
            root = None

            for name, value in data.items():
                match name:
                    case "response":
                        code = int(value)
                    case "message":
                        message = value
                    case "root":
                        root = DirectoryInfo.from_message_dict(dict(value))
            
            if code == None or message == None or root == None:
                raise ValueError("The dictionary does not provide enough information, or the root directory is of invalid format")
            else:
                return DirMessage(code, message, root)

class MoveMessage(MessageBasis):
    def __init__(self, path: str):
        self.__path = path

    def message_type(self) -> MessageType:
        return MessageType.Move
    def data(self) -> dict:
        return {
            "path": self.__path
        }

    def path(self) -> str:
        return self.__path
    
    def parse(data: dict, req: bool = True) -> Self:
        if not req:
            raise ValueError("Move message has no response variant")
        
        path = data["path"]

        if path == None:
            raise ValueError("Not enough data supplied")
        else:
            return MoveMessage(path)
            
class SubfolderAction(Enum):
    Delete = "delete"
    Add = "add"
class SubfolderMessage(MessageBasis):
    def __init__(self, path: str, action: SubfolderAction):
        self.__path = path
        self.__action = action

    def message_type(self) -> MessageType:
        return MessageType.Subfolder
    def data(self) -> dict:
        return {
            "path": self.__path,
            "action": self.__action.value
        }

    def path(self) -> str:
        return self.__path
    def action(self) -> SubfolderAction:
        return self.__action
    
    def parse(data: dict, req: bool = True) -> Self:
        if not req:
            raise ValueError("Subfolder message has no response variant")
        
        try:
            path = data["path"]
            action = SubfolderAction(data["action"])
        except:
            path = None
            action = None

        if path == None or action == None:
            raise ValueError("Not enough data supplied")
        else:
            return SubfolderMessage(path, action)