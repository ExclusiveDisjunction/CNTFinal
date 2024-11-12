from enum import Enum
from typing import Self

class ServerPath:
    pass

class DirectoryInfo:
    def to_dict(self) -> dict:
        return {} 
    def from_message_dict(dict: input) -> Self | None:
        return DirectoryInfo()
    
    def __eq__(self, other) -> bool:
        if other == None:
            return False
        else:
            return True

class FileInfo:
    def __dict__() -> dict:
        return {

        }

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"

