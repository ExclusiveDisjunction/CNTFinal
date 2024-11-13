import os
from ack_codes import AckCodes

def UploadFile(path, data):
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND

    # Check for invalid characters in path
    if '..' in path or path.startswith('/'):
        return AckCodes.FORBIDDEN

    # Normalize path to prevent directory traversal
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith('..'):
        return AckCodes.FORBIDDEN

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

    # Validate path and normalize
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND
    if '..' in path or path.startswith('/'):
        return AckCodes.FORBIDDEN
    normalized_path = os.path.normpath(os.path.join(client_directory, path))
    if normalized_path.startswith('..'):
        return AckCodes.FORBIDDEN

    # Construct the full path
    root_directory = ''  # Replace with actual root directory
    upload_path = os.path.normpath(os.path.join(root_directory, normalized_path, file_name))
    if not upload_path.startswith(root_directory):
        return AckCodes.FORBIDDEN

    # Check if file already exists
    if os.path.exists(upload_path):
        return AckCodes.FILE_ALREADY_EXISTS

    # Check file size
    MIN_FILE_SIZE = 0  # Define appropriate min file size
    if len(file_content) > MIN_FILE_SIZE:
        return AckCodes.BUFFER_TOO_LARGE

    # Save the file and assign ownership
    try:
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        with open(upload_path, 'wb') as f:
            f.write(file_content)
        # Assign ownership metadata
        os.setxattr(upload_path, 'user.owner', owner.encode())
        return AckCodes.OK
    except PermissionError:
        return AckCodes.UNAUTHORIZED
    except Exception:
        return AckCodes.CONFLICT

def DownloadFile(path, data):
    # Validate path and get front-end data
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND, None
    if '..' in path or path.startswith('/'):
        return AckCodes.FORBIDDEN, None
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith('..'):
        return AckCodes.FORBIDDEN, None

    owner = data['owner']
    client_directory = data['client_directory']

    # Construct the full path
    root_directory = ''  # Replace with actual root directory
    download_path = os.path.normpath(os.path.join(root_directory, client_directory, normalized_path))
    if not download_path.startswith(root_directory):
        return AckCodes.FORBIDDEN, None

    # Check if file exists and user owns it
    if not os.path.exists(download_path):
        return AckCodes.NOT_FOUND, None

    try:
        file_owner = os.getxattr(download_path, 'user.owner').decode()
        if file_owner != owner:
            return AckCodes.UNAUTHORIZED, None
        with open(download_path, 'rb') as f:
            file_content = f.read()
        return AckCodes.OK, file_content
    except PermissionError:
        return AckCodes.UNAUTHORIZED, None
    except Exception:
        return AckCodes.CONFLICT, None

def DeleteFile(path, data):
    # Validate path is a string and not empty
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND
    
    # Check for invalid characters in path
    if '..' in path or path.startswith('/'):
        return AckCodes.FORBIDDEN
    
    # Normalize path to prevent directory traversal
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith('..'):
        return AckCodes.FORBIDDEN
    
    # Get required data from front end
    owner = data.get('owner')
    client_directory = data.get('client_directory')
    if not owner or not client_directory:
        return AckCodes.CONFLICT
    
    # Construct the full path
    root_directory = ''  # Replace with actual root directory
    delete_path = os.path.normpath(os.path.join(root_directory, client_directory, normalized_path))
    if not delete_path.startswith(root_directory):
        return AckCodes.FORBIDDEN
    
    # Check if file exists and is not a directory
    if not os.path.exists(delete_path) or os.path.isdir(delete_path):
        return AckCodes.NOT_FOUND
    
    # Check if user owns the file
    try:
        file_owner = os.getxattr(delete_path, 'user.owner').decode()
        if file_owner != owner:
            return AckCodes.UNAUTHORIZED
        # Delete the file
        os.remove(delete_path)
        return AckCodes.OK
    except PermissionError:
        return AckCodes.UNAUTHORIZED
    except Exception:
        return AckCodes.CONFLICT

def MoveDirectory(path, new_path, data):
    # Validate paths are strings and not empty
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND
    if not isinstance(new_path, str) or not new_path:
        return AckCodes.NOT_FOUND
    
    # Check for invalid characters in paths
    if '..' in path or path.startswith('/') or '..' in new_path or new_path.startswith('/'):
        return AckCodes.FORBIDDEN
    
    # Normalize paths to prevent directory traversal
    normalized_path = os.path.normpath(path)
    normalized_new_path = os.path.normpath(new_path)
    if normalized_path.startswith('..') or normalized_new_path.startswith('..'):
        return AckCodes.FORBIDDEN
    
    # Get required data from front end
    owner = data.get('owner')
    current_directory = data.get('current_directory', '')
    if not owner:
        return AckCodes.CONFLICT
    
    # Construct the full paths
    root_directory = ''  # Replace with actual root directory
    source_path = os.path.normpath(os.path.join(root_directory, current_directory, normalized_path))
    destination_path = os.path.normpath(os.path.join(root_directory, current_directory, normalized_new_path))
    if not source_path.startswith(root_directory) or not destination_path.startswith(root_directory):
        return AckCodes.FORBIDDEN
    
    # Check if source directory exists and is a directory
    if not os.path.exists(source_path) or not os.path.isdir(source_path):
        return AckCodes.NOT_FOUND
    
    # Check if destination already exists
    if os.path.exists(destination_path):
        return AckCodes.CONFLICT
    
    # Check if user owns the source directory
    try:
        dir_owner = os.getxattr(source_path, 'user.owner').decode()
        if dir_owner != owner:
            return AckCodes.UNAUTHORIZED
        # Move the directory
        os.rename(source_path, destination_path)
        return AckCodes.OK
    except PermissionError:
        return AckCodes.UNAUTHORIZED
    except Exception:
        return AckCodes.CONFLICT

def ModifySubdirectories(path, subfolder_action, data):
    # Validate path is a string and not empty
    if not isinstance(path, str) or not path:
        return AckCodes.NOT_FOUND
    
    # Check for invalid characters in path
    if '..' in path or path.startswith('/'):
        return AckCodes.FORBIDDEN
    
    # Normalize path to prevent directory traversal
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith('..'):
        return AckCodes.FORBIDDEN
    
    # Get required data from front end
    owner = data.get('owner')
    current_directory = data.get('current_directory', '')
    if not owner or not current_directory:
        return AckCodes.CONFLICT
    
    # Construct the full path
    root_directory = ''  # Replace with actual root directory
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
            return AckCodes.CONFLICT
    except PermissionError:
        return AckCodes.UNAUTHORIZED
    except Exception:
        return AckCodes.CONFLICT