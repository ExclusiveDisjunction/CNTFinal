import os
from enum import Enum
from ack_codes import AckCodes
from file_tracking import CheckFileOwner, ListFiles, Status
from exceptions import *

ROOT_DIRECTORY = 'server_root'

class SubfolderAction(Enum):
    ADD = 'add'
    REMOVE = 'remove'

def UploadFile(path, data):
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND

    # Ensure all required fields are present
    required_fields = ['name', 'file_name', 'kind', 'owner', 'client_directory', 'file_content']
    for field in required_fields:
        if field not in data:
            return AckCodes.CONFLICT

    # Assign variables
    name = data['name']
    file_name = data['file_name']
    file_type = data['kind']
    owner = data['owner']
    client_directory = data['client_directory']
    file_content = data['file_content']

    # Construct the absolute path
    absolute_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, client_directory, path, file_name))

    # Ensure the absolute path is within the root directory
    if not absolute_path.startswith(os.path.abspath(ROOT_DIRECTORY)):
        return AckCodes.FORBIDDEN

    # Check if file already exists
    if os.path.exists(absolute_path):
        return AckCodes.FILE_ALREADY_EXISTS
    
    # After checking if file already exists
    if os.path.isdir(absolute_path):
        raise ConflictError("A directory with the same name exists.")

    # Validate file type if necessary
    allowed_file_types = ['txt', 'mp3', 'mp4']  # Allowed types
    if file_type not in allowed_file_types:
        raise ConflictError("Invalid file type.")

    # Save the file and assign ownership
    try:
        os.makedirs(os.path.dirname(absolute_path), exist_ok=True)
        with open(absolute_path, 'wb') as f:
            f.write(file_content)
        set_file_owner(absolute_path, owner)
        return AckCodes.OK
    except PermissionError:
        return AckCodes.UNAUTHORIZED
    except Exception:
        return AckCodes.CONFLICT

def DownloadFile(path, data):
    if not isinstance(path, str) or not path:
        raise NotFoundError("Invalid path.")

    owner = data.get('owner')
    client_directory = data.get('client_directory')

    # Construct the absolute path
    absolute_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, client_directory, path))

    # Ensure the absolute path is within the root directory
    if not absolute_path.startswith(os.path.abspath(ROOT_DIRECTORY)):
        raise PathInvalidError("Attempted to access outside of root directory.")

    # Check if file exists and is not a directory
    if not os.path.exists(absolute_path) or os.path.isdir(absolute_path):
        raise NotFoundError("File not found.")

    # Check if user owns the file
    owner_status = CheckFileOwner(absolute_path, owner)
    if owner_status != Status.SUCCESS:
        raise UnauthorizedError("User does not own the file.")

    # Read and return the file content
    try:
        with open(absolute_path, 'rb') as f:
            file_content = f.read()
        return file_content
    except PermissionError:
        raise UnauthorizedError("Permission denied.")
    except Exception:
        raise ConflictError("Could not read the file.")

def DeleteFile(path, data):
    if not isinstance(path, str) or not path:
        raise NotFoundError("Invalid path.")

    owner = data.get('owner')
    client_directory = data.get('client_directory')

    # Construct the absolute path
    absolute_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, client_directory, path))

    # Ensure the absolute path is within the root directory
    if not absolute_path.startswith(os.path.abspath(ROOT_DIRECTORY)):
        raise PathInvalidError("Attempted to access outside of root directory.")

    # Check if file exists and is not a directory
    if not os.path.exists(absolute_path) or os.path.isdir(absolute_path):
        raise NotFoundError("File not found.")

    # Check if user owns the file
    owner_status = CheckFileOwner(absolute_path, owner)
    if owner_status != Status.SUCCESS:
        raise UnauthorizedError("User does not own the file.")

    # Delete the file
    try:
        os.remove(absolute_path)
    except PermissionError:
        raise UnauthorizedError("Permission denied.")
    except Exception:
        raise ConflictError("Could not delete the file.")

def MoveItem(path, new_path, data):
    # Validate paths are strings and not empty
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND
    if not isinstance(new_path, str) or not new_path:
        return AckCodes.NOT_FOUND
    
    # Construct absolute paths
    source_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, client_directory, path))
    destination_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, client_directory, new_path))

    # Ensure paths are within the root directory
    if not source_path.startswith(os.path.abspath(ROOT_DIRECTORY)) or not destination_path.startswith(os.path.abspath(ROOT_DIRECTORY)):
        raise PathInvalidError("Attempted to access outside of root directory.")

    # Check if source exists
    if not os.path.exists(source_path):
        raise NotFoundError("Source not found.")

    # Check if user owns the source
    owner_status = CheckFileOwner(source_path, owner)
    if owner_status != Status.SUCCESS:
        raise UnauthorizedError("User does not own the source item.")

    # Check if destination exists
    if os.path.exists(destination_path):
        raise ConflictError("Destination already exists.")

    # Move the item
    try:
        os.rename(source_path, destination_path)
    except PermissionError:
        raise UnauthorizedError("Permission denied.")
    except Exception:
        raise ConflictError("Could not move the item.")

def ModifySubdirectories(path, subfolder_action, data):
    # Validate path is a string and not empty
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND
    
    absolute_path = os.path.abspath(os.path.join(root_directory, client_directory, path))
    if not absolute_path.startswith(os.path.abspath(root_directory)):
        return AckCodes.FORBIDDEN
    
    # Get required data from front end
    owner = data.get('owner')
    current_directory = data.get('current_directory', '')
    if not owner or not current_directory:
        return AckCodes.CONFLICT
    
    # Construct the full path
    root_directory = ROOT_DIRECTORY
    target_path = os.path.normpath(os.path.join(root_directory, current_directory, normalized_path))
    if not target_path.startswith(root_directory):
        return AckCodes.FORBIDDEN
    
    # Check if action is valid
    if subfolder_action not in SubfolderAction:
        return AckCodes.CONFLICT
    
    # Perform action
    try:
        if subfolder_action == SubfolderAction.ADD:
            if os.path.exists(target_path):
                return AckCodes.CONFLICT
            os.makedirs(target_path, exist_ok=False)
            # Assign ownership metadata
            os.setxattr(target_path, 'user.owner', owner.encode())
            return AckCodes.OK
        elif subfolder_action == SubfolderAction.REMOVE:
            if not os.path.exists(target_path) or not os.path.isdir(target_path):
                return AckCodes.NOT_FOUND
            dir_owner = os.getxattr(target_path, 'user.owner').decode()
            if dir_owner != owner:
                return AckCodes.UNAUTHORIZED
            os.rmdir(target_path)
            return AckCodes.OK
        else:
            raise ConflictError("Invalid subfolder action.")
    except PermissionError:
        return AckCodes.UNAUTHORIZED
    except Exception:
        return AckCodes.CONFLICT

def ListFilesWrapper(path):
    return ListFiles(path)

# file_io.py
def GetFileSize(path, data):
    if not isinstance(path, str) or not path:
        raise NotFoundError("Invalid path.")

    owner = data.get('owner')
    client_directory = data.get('client_directory')

    # Construct the absolute path
    absolute_path = os.path.abspath(os.path.join(ROOT_DIRECTORY, client_directory, path))

    # Ensure the absolute path is within the root directory
    if not absolute_path.startswith(os.path.abspath(ROOT_DIRECTORY)):
        raise PathInvalidError("Attempted to access outside of root directory.")

    # Check if file exists
    if not os.path.exists(absolute_path) or os.path.isdir(absolute_path):
        raise NotFoundError("File not found.")

    # Check if user owns the file
    owner_status = CheckFileOwner(absolute_path, owner)
    if owner_status != Status.SUCCESS:
        raise UnauthorizedError("User does not own the file.")

    # Get the file size
    try:
        size = os.path.getsize(absolute_path)
        return size
    except Exception:
        raise ConflictError("Could not retrieve file size.")
