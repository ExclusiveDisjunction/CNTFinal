import json
from enum import Enum

from ..Server.server_path import DirectoryInfo, FileType

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

def make_basis(command: MessageType, request: bool = True) -> dict:
    if request:
        direction = "request"
    else:
        direction = "response"

    result = {
        "command": command.value,
        "direction": direction,
        "data": {

        }
    }
    return result

def make_connect(username: str, passwordHash: str) -> str:
    result = make_basis(MessageType.Connect)
    result["data"]["username"] = username 
    result["data"]["password"] = passwordHash

    return json.dumps(result)
def make_close() -> str:
    result = make_basis(MessageType.Close)

    return json.dumps(result)
def make_ack(code: int, message: str) -> str:
    result = make_basis(MessageType.ack)
    result["data"]["code"] = code 
    result["data"]["message"] = message

    return json.dumps(result)

def make_move(path: str) -> str:
    result = make_basis(MessageType.Move)

    result["data"]["path"] = path

    return json.dumps(result)
def make_delete(path: str) -> str:
    result = make_basis(MessageType.Delete)

    result["data"]["path"] = path

    return json.dumps(result)

def make_subfolder(path: str, create: bool) -> str:
    result = make_basis(MessageType.Subfolder)

    result["data"]["path"] = path
    if create:
        result["data"]["action"] = "add"
    else:
        result["data"]["action"] = "delete"

    return json.dumps(result)

def make_dir_request() -> str:
    result = make_basis(MessageType.Dir)

    return json.dumps(result)
def make_dir_response(code: int, message: str, rootDir: DirectoryInfo) -> str:
    result = make_basis(MessageType.Dir, False)

    result["data"]["response"] = code
    result["data"]["message"] = message
    result["data"]["root"] = rootDir.to_message_dict()

    return json.dumps(result)

def make_upload_req(name: str, kind: FileType, size: int) -> str:
    result = make_basis(MessageType.Upload)

    result["data"]["name"] = name
    result["data"]["kind"] = kind.value 
    result["data"]["size"] = size

    return json.dumps(result)

def make_download_req(path: str) -> str:
    result = make_basis(MessageType.Download)

    result["data"]["path"] = path

    return json.dumps(result)
def make_download_resp(status: int, message: str, kind: FileType | None = None, size: int | None = None):
    result = make_basis(MessageType.Download, False)

    result["data"]["status"] = status
    result["data"]["message"] = message
    if kind == None or size == None:
        result["data"]["format"] = dict()
    elif kind == None or size == None: # Information missing
        raise ValueError("Either kind or size is none, this is not allowed")
    else:
        result["data"]["format"] = {
            "kind": kind.value,
            "size": size
        }

    return json.dumps(result)

def parse_message(text: str) -> tuple[MessageType, bool, dict] | None:
    """
        Obtains the decoded message from a JSON formatted string. If the boolean memember result is true, it is a request.
        Returns None if the format is invalid.
    """

    try:
        decoded = json.loads(text)
    except:
        return None

    msg_type_s = None
    req = None
    data = None
    for k, v in decoded.items():
        if k == "convention":
            msg_type_s = v
        elif k == "direction":
            if v == "request":
                req = True
            else:
                req = False
        elif k == "data":
            data = v

    if msg_type_s == None or req == None or data == None:
        return None
    
    match msg_type_s:
        case "connect":
            msg_type = MessageType.Connect
        case "close":
            msg_type = MessageType.Close
        case "ack":
            msg_type = MessageType.Ack
        case "upload":
            msg_type = MessageType.Upload
        case "download":
            msg_type = MessageType.Download
        case "delete":
            msg_type = MessageType.Delete
        case "dir":
            msg_type = MessageType.Dir
        case "move":
            msg_type = MessageType.Move
        case "subfolder":
            msg_type = MessageType.Subfolder

    return (
        msg_type_s,
        req,
        data
    )
