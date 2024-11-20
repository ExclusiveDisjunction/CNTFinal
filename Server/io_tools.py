from Common.file_io import FileType, get_file_type
from typing import Self
from pathlib import Path
import json
import os

from .credentials import Credentials
from .server_paths import root_directory
from Common.file_io import FileInfo, DirectoryInfo, get_file_total_size

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
class FileOwnerDB:
    def __init__(self):
        self.__path = None
        self.__data = None

    def open(self, path: Path):
        if not path.exists():
            try:
                path.touch()
            except:
                raise ValueError("Could not open file at that path")
        
        with open(path, 'r') as f:
            contents = f.read()
        
        if not contents or len(contents) == 0:
            contents = "{}"
        
        self.__data = dict(json.loads(contents))
        self.__path = path

    def get_file_owner(self, path: Path, is_absolute: bool = True) -> Credentials | None:
        if is_absolute:
            path = make_relative(path)

        if path is None:
            return None
        
        result = self.__data.get(str(path))
        if result is None:
            return None
        else:
            return Credentials(result["username"], result["password"])
    def set_file_owner(self, path: Path, credentials: Credentials, is_absolute: bool = True):
        if is_absolute:
            path = make_relative(path)

        if path is None:
            raise ValueError("The path provided is not valid")
        
        self.__data[str(path)] = {
            "username": credentials.getUsername(),
            "password": credentials.getPasswordHash()
        }

    def save(self):
        with open(self.__path, 'w') as f:
            f.write(json.dumps(self.__data))

file_owner_db = FileOwnerDB()

def is_file_owner(path: Path, user: Credentials) -> bool:
    global file_owner_db

    result = file_owner_db.get_file_owner(path)
    return result is not None and result == user

# Directory Managment
def contents_to_list(path: Path) -> list[DirectoryInfo | FileInfo]:
    global file_owner_db
    result = []

    for entry in os.listdir(path):
        try:

            full_path = (path / entry).resolve()
            if full_path.is_dir():
                target = DirectoryInfo(entry)
                target.set_contents(contents_to_list(full_path))

                result.append(target)
            elif full_path.is_file():
                raw_owner = file_owner_db.get_file_owner(full_path)
                if raw_owner is None:
                    owner = ""
                else:
                    owner = raw_owner.getUsername()
                result.append(
                    
                    FileInfo(entry, owner, get_file_type(full_path), get_file_total_size(full_path))
                )
        except:
            continue

    return result

def create_directory_info(start_path: Path = None) -> DirectoryInfo:
    """Create directory info starting from specified path"""
    global root_directory
    
    if start_path is None:
        start_path = root_directory
    
    base_name = start_path.name if start_path != root_directory else "root"
    result = DirectoryInfo(base_name)
    result.set_contents(contents_to_list(start_path))
    return result
