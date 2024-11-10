import json
from enum import Enum

class MessageType(Enum):
    Greet = "greet"
    Upload = "upload"
    Download = "download"
    Delete = "delete"
    Dir = "dir"
    Move = "move"
    Subfolder = "subfolder"


