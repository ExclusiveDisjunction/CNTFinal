import os
import json
from enum import Enum
from file_io import ROOT_DIRECTORY
from directory_info import DirectoryInfo, FileInfo

class Status(Enum):
    FILE_NOT_FOUND = 'File not found'
    PATH_INVALID = 'Path invalid'
    UNAUTHORIZED = 'Unauthorized'
    SUCCESS = 'Success'

# Make a method for initalizing a directory??

def GetDirectoryStructure():
    root_dir = ROOT_DIRECTORY

    def dir_to_dict(path):
        dir_owner = get_directory_owner(path)
        dir_info = DirectoryInfo(name=os.path.basename(path), owner=dir_owner)
        try:
            for entry in os.listdir(path):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    dir_info.add_content(dir_to_dict(full_path))
                else:
                    file_owner = get_file_owner(full_path)
                    file_type = get_file_type(full_path)
                    file_size = os.path.getsize(full_path)
                    file_info = FileInfo(
                        name=entry,
                        file_type=file_type,
                        owner=file_owner,
                        size=file_size
                    )
                    dir_info.add_content(file_info)
        except PermissionError:
            pass
        return dir_info
    directory_info = dir_to_dict(root_dir)
    return directory_info

def CheckFileOwner(path, user):
    if not os.path.exists(path):
        return Status.FILE_NOT_FOUND
    file_owner = get_file_owner(path)
    if file_owner == user:
        return Status.SUCCESS
    else:
        return Status.UNAUTHORIZED

def ListFiles(path):
    if not os.path.exists(path):
        return Status.PATH_INVALID
    entries = []
    try:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                entries.append({'type': 'directory', 'name': entry})
            else:
                entries.append({'type': 'file', 'name': entry})
    except PermissionError:
        return Status.UNAUTHORIZED
    return entries  # Return files and subfolders in specified format

def get_file_owner(path):
    try:
        return os.getxattr(path, 'user.owner').decode()
    except (OSError, AttributeError):
        return None

def set_file_owner(path, owner):
    try:
        os.setxattr(path, 'user.owner', owner.encode())
        return True
    except (OSError, AttributeError):
        return False
