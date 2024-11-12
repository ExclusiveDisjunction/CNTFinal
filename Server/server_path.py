from enum import Enum
from typing import Self
from pathlib import Path
import os
from Server.credentials import Credentials

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"

class FileInfo:
    """
    A structure that contains the path & allows for relative moving
    """

    def __init__(self, relative_path: Path | str, owner: Credentials, kind: FileType):
        if relative_path == None:
            raise ValueError("The path supplied must be valid and a file")
        
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)
        
        self.__path = relative_path
        self.__owner = owner
        self.__kind = kind

    def to_dict(self) -> dict:
        return {
            "kind": "file",
            "name": self.__path.name,
            "file_kind": self.__kind.value,
            "owner": self.__owner.getUsername()
        }
    def from_dict(data: dict) -> Self:
        try:
            path = Path(data["name"])
            file_kind = FileType(data["file_kind"])
            owner = Credentials(data["owner"], str())
        except:
            path = None
            file_kind = None
            owner = None

        if path == None or file_kind == None or owner == None:
            raise ValueError("The dictionary does not contain enough data to fill this structure")
        
    
    def __eq__(self, other) -> bool:
        if self == None and other == None:
            return True
        elif self == None or other == None:
            return False
        
        return self.__path == other.__path and self.__owner == other.__owner
    
    def name(self) -> str:
        return self.__path.name
    def kind(self) -> FileType:
        return self.__kind
    def owner(self) -> Credentials:
        return self.__owner
    def get_size(self) -> int | None: 
        if not self.__path.exists():
            return None
        
        return os.path.getsize(self.__path)
        
    def correct_path(self, parent: Path): 
        self.__path = parent.joinpath(self.__path)
    
    def target_path_relative(self) -> Path:
        """
        Returns the current path relative to the root
        """
        return self.__path
    def target_path_absolute(self, env_path: Path) -> str:
        """
        Returns the current path relative to the OS root
        """
        return env_path + self.__path

class DirectoryInfo:
    def __init__(self, relative_path: Path, files: list[FileInfo] | None, dirs: list[Self] | None):
        if relative_path == None:
            raise ValueError("The path supplied must be valid and a file")
        
        if isinstance(relative_path, str):
            relative_path = Path(relative_path)

        self.__path = relative_path
        self.__files = files
        self.__dirs = dirs

    def to_dict(self) -> dict:
        contents = []
        for dir in self.__dirs:
            contents.append(dir.to_dict())
        for file in self.__files:
            contents.append(file.to_dict())

        return {
            "kind": "directory",
            "name": self.get_name(),
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
        
        if name == "root":
            path = Path("")
        else:
            path = Path(name)
        
        files = []
        dirs = []
        for info in contents:
            if info["kind"] == "directory":
                files.append(DirectoryInfo.from_dict(info))
            elif info["kind"] == "file":
                dirs.append(FileInfo.from_dict(info))

        return DirectoryInfo(path, files, dirs)
    
    def correct_path(self, parent: Path, is_root: bool = True):
        if is_root:
            self.__path = Path("")
        else:
            self.__path = parent.joinpath(self.__path)

        dirs, files = self.get_child_directories(), self.get_child_files()
        for dir in dirs:
            dir.correct_path(self.__path, False)
        for file in files:
                file.correct_path(self.__path)

    
    def __eq__(self, other) -> bool:
        if other == None:
            return False
        else:
            return True
        
    def get_path(self):
        return self.__path
    def get_name(self) -> str:
        if self.__path == "":
            return "root"
        else:
            return self.__path.name
        
    def get_child_directories(self) -> list[Self] | None:
        return self.__dirs
    def get_child_files(self) -> list[FileInfo] | None:
        return self.__files
