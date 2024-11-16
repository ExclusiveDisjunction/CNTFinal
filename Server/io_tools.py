from enum import Enum
from typing import Self
from pathlib import Path
import os

from .credentials import Credentials

class Status(Enum):
    FILE_NOT_FOUND = 'File not found'
    PATH_INVALID = 'Path invalid'
    UNAUTHORIZED = 'Unauthorized'
    SUCCESS = 'Success'

root_directory = Path.home() / "cnt" / "data"

def ensure_root_directory() -> bool:
    global root_directory
    
    try:
        if not root_directory.exists():
            os.makedirs(root_directory)
        return True
    except:
        return False

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"

class FileInfo:
    """
    A structure that contains the path & allows for relative moving
    """

    def __init__(self, name: str | str, owner_username, kind: FileType, size: int, parent = None):
        self.__parent = parent
        self.__name = name
        self.__owner = owner_username
        self.__kind = kind

    def to_dict(self) -> dict:
        return {
            "kind": "file",
            "name": self.__name,
            "file_kind": self.__kind.value,
            "owner": self.__owner
        }
    def from_dict(data: dict, parent = None) -> Self:
        try:
            name = data["name"]
            file_kind = FileType(data["file_kind"])
            owner = data["owner"]
        except:
            name = None
            file_kind = None
            owner = None

        if name == None or file_kind == None:
            raise ValueError("The dictionary does not contain enough data to fill this structure")
        
        return FileInfo(name, owner, file_kind, parent)
          
    def __eq__(self, other) -> bool:
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        
        return self.__name == other.__name and self.__owner == other.__owner and self.__kind == other.__kind
    
    def name(self) -> str:
        return self.__name
    def kind(self) -> FileType:
        return self.__kind
    def owner_username(self) -> str:
        return self.__owner
    def parent(self):
        return self.__parent
    def set_parent(self, parent):
        self.__parent = parent
    
    def target_path_relative(self) -> Path:
        """
        Returns the current path relative to the root
        """

        if self.__parent is None:
            return None
        
        return self.__parent.targt_path_relative().joinpath(self.__name)
    
    def target_path_absolute(self, env_path: Path) -> str:
        """
        Returns the current path relative to the OS root
        """
        return env_path.joinpath(self.target_path_relative())

class DirectoryInfo:
    def __init__(self, name: str, contents: list[FileInfo | Self] | None = None, parent: Self | None = None):
        self.__name = name
        if contents is None:
            self.__contents = []
        else:
            self.__contents = contents

        self.__parent = parent

        # Build proper order
        for content in self.__contents:
            if content is not None:
                content.set_parent(self)

    def to_dict(self) -> dict:
        contents = []
        for item in self.__contents:
            contents.append(item.to_dict())
        return {
            "kind": "directory",
            "name": self.__name,
            "contents": contents
        } 
    def from_dict(data: dict) -> Self | None:
        try:
            name = data["name"]
            contents = list(data["contents"])
        except:
            name = None
            contents = None
        
        if name == None or contents == None:
            raise ValueError("The contents could not be read")
        
        trueContents = []
        for info in contents:
            if info["kind"] == "directory":
                trueContents.append(DirectoryInfo.from_dict(info))
            elif info["kind"] == "file":
                trueContents.append(FileInfo.from_dict(info))

        return DirectoryInfo(name, trueContents)
    
    def __eq__(self, other) -> bool:
        if other is None and self is None:
            return True
        elif other is None or self is None:
            return False
        else:
            return self.__name == other.__name and self.__files == other.__files and self.__dirs == other.__dirs
        
    def name(self) -> str:
        return self.__name
    def parent(self) -> Self | None:
        return self.__parent
    def set_parent(self, parent: Self | None):
        self.__parent = parent

    def target_path_relative(self) -> Path:
        """
        Returns the current path relative to the root
        """

        if self.__parent is None:
            return Path("")
        else:
            return self.__parent.target_path_relative().joinpath(self.__name)
    
    def target_path_absolute(self, env_path: Path) -> str:
        """
        Returns the current path relative to the OS root
        """
        return env_path.joinpath(self.target_path_relative())
        
    def add_content(self, content):
        self.__contents.append(content)
    def contents(self):
        return self.__contents
    def set_contents(self, contents: list[Self | FileInfo] | None):
        if contents is None:
            self.__contents = []
        else:
            self.__contents = contents

# Directory Managment
def contents_to_list(path: Path) -> list[DirectoryInfo | FileInfo]:
    result = []

    for entry in os.listdir(path):
        try:

            full_path = (path / entry).resolve()
            if full_path.is_dir():
                target = DirectoryInfo(entry)
                target.set_contents(contents_to_list(full_path))

                result.append(target)
            elif full_path.is_file():
                result.append(
                    FileInfo(entry, get_file_owner(full_path), get_file_type(full_path), get_file_size(full_path))
                )
        except:
            continue

    return result

def create_directory_info() -> DirectoryInfo:
    global root_directory

    result = DirectoryInfo("root")

    result.set_contents(contents_to_list(root_directory))
    return result

# Path Management
def move_relative(raw_path: str, curr_dir: Path) -> Path | None:
    """
    Moves to the raw_path relative to the curr_dir. It returns the absolute path.
    """
    if raw_path is None or curr_dir is None:
        return None
    
    path = Path(raw_path)
    if path.is_absolute():
        return None
    
    new_path = curr_dir.joinpath(path)
    return new_path.resolve()

def make_relative(path: Path) -> Path | None:
    """
    Determines the absolute path as a relative one. It is relative to the root_directory.
    """
    global root_directory
    
    if not is_path_valid(path):
        return None
    
    return remove_from_front_path(path, len(root_directory.parts))

def remove_from_front_path(path: Path, n_remove: int) -> Path | None:
    """
    Removes a specified number of elements from the start of a path
    """
    if path is None or n_remove < 0 or n_remove > len(path.parts):
        return None
    elif n_remove == len(path.parts):
        return Path("")
    
    extracted = path.parts[n_remove:]
    if len(extracted) == 0:
        return Path()
    else:
        return Path('/'.join(extracted))

def is_path_valid(path: Path) -> bool:
    """
    Determines if a path lives inside of the root_directory. 
    """
    global root_directory

    target_size = len(root_directory.parts)
    if len(path.parts) == target_size:
        return True
    elif len(path.parts) < target_size:
        return False
    else:
        return path.parts[0:target_size] == root_directory.parts

# File management
def get_file_owner(path) -> str:
    try:
        # return os.getxattr(path, 'user.owner').decode()
        pass
    except (OSError, AttributeError):
        return None
    
def set_file_owner(path, owner: Credentials) -> bool:
    try:
        # os.setxattr(path, 'user.owner', owner.getUsername().encode())
        return True
    
    except (OSError, AttributeError):
        return False  
    
def is_file_owner(path: Path, user: Credentials) -> bool:
    if path is None or user is None or not path.exists():
        return False

    file_owner = get_file_owner(path)
    return True
    #return file_owner == user.getUsername()
    
def get_file_type(path: Path) -> FileType | None:
    if path is None:
        return None
    
    match path.suffix:
        case (".mp4", ".mov", ".avi", ".wmv"):
            return FileType.Video
        case (".mp3", ".wav", ".aac", ".flac", ".aiff"):
            return FileType.Audio
        case _:
            return FileType.Text
        
def get_file_size(path: Path | str) -> int | None:
    if path is None:
        return None
    
    if isinstance(path, str):
        path = Path(path)
    
    if not path.is_file():
        return None
    
    try:
        return os.path.getsize(path)
    except:
        return None