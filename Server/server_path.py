from enum import Enum

class ServerPath:
    pass

class DirectoryInfo:
    def to_message_dict() -> dict:
        return dict()

class FileInfo:
    pass

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"