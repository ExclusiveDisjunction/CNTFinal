from enum import Enum
from typing import Self

class ServerPath:
    pass

class DirectoryInfo:
    def to_dict(self) -> dict:
        return {} 
    def from_message_dict(self, dict: input) -> Self | None:
        pass

class FileInfo:
    def __dict__() -> dict:
        return {

        }

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"

