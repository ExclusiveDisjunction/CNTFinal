import os
from pathlib import Path

from Common.http_codes import *
from Common.message_handler import SubfolderAction
from .credentials import Credentials
from .io_tools import is_path_valid, is_file_owner

class UploadHandle:
    def __init__(self, path: Path, owner: Credentials):
        self.path = path
        self.owner = owner

def RequestUpload(path: Path, curr_user: Credentials) -> UploadHandle | HTTPErrorBasis: 
    if path is None or curr_user is None or not path.exists() or not path.is_file():
        return NotFoundError()

    if not is_path_valid(path):
        return ForbiddenError()

    # At this point, we are ok for writing. Send a response back to the front end.
    try:
        os.mkdirs(os.path.dirname(path), exist_ok = True)
        return UploadHandle(path, curr_user)
    except PermissionError:
        return UnauthorizedError("The system does not have access to the resource specified")
    except:
        return ConflictError("File aready exists")
    
def UploadFile(handle: UploadHandle, content) -> bool:
    if handle is None or not handle.path.exists():
        return False

    try:
        f = open(handle.path, 'wb')
        f.write(content)

        f.close()
        return True
    except:
        return False

def ExtractFileContents(path: Path, curr_user: Credentials) -> str | HTTPErrorBasis:
    if path is None or not path.exists:
        return FileNotFoundError()
    elif curr_user is None or not is_file_owner(path, curr_user):
        return UnauthorizedError()
    elif not is_path_valid(path):
        return ForbiddenError()
    
    try:
        f = open(path, 'rb')
        content = f.read()

        f.close()  
        return content
    except PermissionError:
        return UnauthorizedError()
    except:
        return ConflictError("Could not read file")

def DeleteFile(path: Path, curr_user: Credentials) -> None | HTTPErrorBasis:
    """
    Deletes a specified path from the file system. This returns None, it was sucessful. Othersie, an error is returned. 
    """
    if path is None or not path.exists():
        return FileNotFoundError()
    elif curr_user is None or not is_file_owner(path, curr_user):
        return UnauthorizedError()
    elif not is_path_valid(path):
        return ForbiddenError()
    
    try:
        os.remove(path)
    except PermissionError:
        return UnauthorizedError("Permission denied")
    except Exception:
        return ConflictError("Could not delete the file")


def ModifySubdirectories(path: Path, action: SubfolderAction) -> None | HTTPErrorBasis:
    if path is None:
        return FileNotFoundError()
    elif not is_path_valid(path):
        return ForbiddenError()
    
    match action:
        case SubfolderAction.Add:
            if path.exists():
                return ConflictError("Path does exist, but attempted to create it")
            
            os.makedirs(action, exist_ok=True)

        case SubfolderAction.Delete:
            if not path.exists():
                return ConflictError("Path does not exist, but attempted to delete")
            
            os.remove(path)
