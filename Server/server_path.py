from enum import Enum
from typing import Self

class ServerPath:
    pass

class DirectoryInfo:
    def to_message_dict() -> dict:
        pass
    def from_message_dict(dict: input) -> Self | None:
        pass

class FileInfo:
    pass

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"