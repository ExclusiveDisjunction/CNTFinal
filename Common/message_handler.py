import json
from enum import Enum
from typing import Self, Any
from pathlib import Path

from Server.io_tools import FileType

"""

This module handles the encoding/decoding of client/server messages to and from JSON formats. It conforms to the format.md file provided. 

"""

class MessageType(Enum):
    """
    Describes the type of message & its short hand used in the file
    """

    Connect = "connect"
    Close = "close"
    Ack = "ack"
    Upload = "upload"
    Download = "download"
    Delete = "delete"
    Dir = "dir"
    Move = "move"
    Subfolder = "subfolder"
    Stats = "stats"

class MessageBasis:
    """
    A base class that provides the functionality of the other Message classes
    """

    def message_type(self) -> MessageType:
        raise NotImplementedError()
    def data(self) -> dict:
        """
        Returns the data member of the message, if the mode is 'request'
        """
        return {}
    def data_response(self) -> dict:
        """
        Returns the data member of the message, if the mode is 'response'
        """
        return {}
    
    def __eq__(self, other: Self) -> bool:
        try:
            return self.message_type() == other.message_type() and self.data() == other.data() and self.data_response() == other.data_response()
        except:
            return False
    
    def construct_message_json(self, request: bool = True) -> str:
        """
        Encodes the message as a JSON file.
        """
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
    
    def parse_from_json(message: str) -> Self | None:
        """
        Converts a JSON encoded string back into a specified Message type. Upon error, it will return None
        """
        try:
            decoded = json.loads(message)
        except:
            return None

        try:
            # Extract the basic information out of the file

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
        
        # We will use the different classes parsers to finish decoding
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
                case MessageType.Stats:
                    return StatsMessage.parse(data, req)
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
        self.__code = int(code)
        self.__message = message

    def message_type(self) -> MessageType:
        return MessageType.Ack
    def data(self) -> dict:
        return self.data_response()
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
        self.__name = str(name)
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

            raw_size = data["size"]
            if raw_size is None:
                size = 0
            else: 
                size = int(raw_size)
        except:
            name = None
            kind = None
            size = None
        
        if name == None or kind == None or size == None:
            raise ValueError("The dictionary provided does not supply enough information")
        
        return UploadMessage(name, kind, size)

class DownloadMessage(MessageBasis):
    def __init__(self, *args):
        """
        If the arguments contains one element, it expects the path for a request. If it contains 4 elements, it expects the status code, message, file kind, and file size. The file kind and file size must either be a value, or none. It cannot be a mixed state.
        """

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
    def __init__(self, path: str | Path):
        self.__path = Path(path)

    def message_type(self) -> MessageType:
        return MessageType.Delete
    def data(self) -> dict:
        return {
            "path": str(self.__path)
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
        """
        If no arguments are provided, the message is a request. Otherwise, it expects 4 arguments: code, message, curr_dir, and size. 
        """

        if len(args) == 0:
            self.__is_response = False
        elif len(args) == 4:
            code = args[0]
            message = args[1]

            curr_dir_raw = args[2]
            size_raw = args[3]

            if curr_dir_raw is None:
                curr_dir = Path("")
            elif not isinstance(curr_dir_raw, Path):
                curr_dir = Path(curr_dir_raw)
            else:
                curr_dir = curr_dir_raw
            
            if size_raw is None:
                size = 0
            elif not isinstance(size_raw, int):
                size = int(size)
            else:
                size = size_raw

            self.__is_response = True
            self.__code = code
            self.__message = message
            self.__curr_dir = curr_dir
            self.__size = size
        else:
            raise ValueError("Not enough arguments or too many")

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
            "curr_dir": str(self.__curr_dir),
            "size": self.__size
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
    def curr_dir(self) -> str | None:
        if self.is_request():
            return None
        else:
            return self.__curr_dir
    def size(self) -> int | None:
        if self.is_request():
            return None
        else:
            return self.__size
    
    def parse(data: dict, req: bool = True) -> Self:
        if req:
            return DirMessage()
        else:
            try:
                code = int(data["response"])
                message = data["message"]
                curr_dir = data["curr_dir"]
                size = int(data["size"])
            except:
                code = None
                message = None
                curr_dir = None
                size = None

            if code == None or message == None or curr_dir == None or size == None:
                raise ValueError("The dictionary does not provide enough information, or the root directory is of invalid format")
            else:
                return DirMessage(code, message, curr_dir, size)

class MoveMessage(MessageBasis):
    def __init__(self, path: Path | str):
        self.__path = Path(path)

    def message_type(self) -> MessageType:
        return MessageType.Move
    def data(self) -> dict:
        return {
            "path": str(self.__path)
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
    def __init__(self, path: Path | str, action: SubfolderAction):
        self.__path = Path(path)
        self.__action = action

    def message_type(self) -> MessageType:
        return MessageType.Subfolder
    def data(self) -> dict:
        return {
            "path": str(self.__path),
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
        
class StatsMessage(MessageBasis):
    def __init__(self, *args):
        """
        If the args contains no elements, it is a request. Otherwise, it expexts the data rates, file transfer times, and latency.
        """

        if len(args) == 0:
            self.__request = True
            self.__data_rates = None
            self.__file_transfer_time = None
            self.__latency = None

        elif len(args) == 3:
            self.__request = False

            self.__data_rates = args[0]
            self.__file_transfer_time = args[1]
            self.__latency = args[2]

        else:
            raise ValueError("Too many or not enough arguments")
        
    def message_type(self) -> MessageType:
        return MessageType.Stats
    def data(self) -> dict:
        return {}
    def data_response(self) -> dict:
        return {
            "data_rate": self.__data_rates,
            "file_transfer": self.__file_transfer_time,
            "latency": self.__latency
        }
    
    def is_request(self) -> bool:
        return self.__request
    def is_response(self) -> bool:
        return not self.__request
    
    def data_rates(self) -> Any | None:
        return self.__data_rates
    def file_transfer_time(self) -> Any | None:
        return self.__file_transfer_time
    def latency(self) -> Any | None:
        return self.__latency
    
    def parse(data: dict, req: bool = True) -> Self:
        if req:
            return StatsMessage()
        else:
            try:
                data_rates = data["data_rate"]
                file_transfer = data["file_transfer"]
                latency = data["latency"]
            except:
                data_rates = None
                file_transfer = None
                latency = None

            if data_rates == None or file_transfer == None or latency == None:
                raise ValueError("The dictionary does not provide enough information, or the root directory is of invalid format")
            else:
                return StatsMessage(data_rates, file_transfer, latency)