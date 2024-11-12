from enum import Enum
from typing import Self
from pathlib import Path
import os

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"

class FileInfo:
    """
    A structure that contains the path & allows for relative moving
    """

    def __init__(self, name: str | str, owner_username, kind: FileType, parent = None):
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

        if name == None or file_kind == None or owner == None:
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
    def get_size(self, env_path: Path) -> int | None: 
        path = self.target_path_absolute(env_path)
        if path is None or not path.exists():
            return None
        
        return os.path.getsize(self.__path)
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
    def __init__(self, name: str, files: list[FileInfo] | None, dirs: list[Self] | None, parent: Self | None = None):
        self.__name = name
        self.__files = files
        self.__dirs = dirs
        self.__parent = parent

        # Build proper order
        for file in self.__files:
            if file is not None:
                file.set_parent(self)
        for dir in self.__dirs:
            if dir is not None:
                dir.set_parent(self)

    def to_dict(self) -> dict:
        contents = []
        for dir in self.__dirs:
            contents.append(dir.to_dict())
        for file in self.__files:
            contents.append(file.to_dict())

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
        
        files = []
        dirs = []
        for info in contents:
            if info["kind"] == "directory":
                dirs.append(DirectoryInfo.from_dict(info))
            elif info["kind"] == "file":
                files.append(FileInfo.from_dict(info))

        return DirectoryInfo(name, files, dirs)
    
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
        
    def get_child_directories(self) -> list[Self] | None:
        return self.__dirs
    def get_child_files(self) -> list[FileInfo] | None:
        return self.__files
