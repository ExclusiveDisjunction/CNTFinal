from file_io import UploadFile, DownloadFile, DeleteFile, MoveDirectory, ModifySubdirectories, ListFilesWrapper, GetFileSize
from file_tracking import CheckFileOwner, get_directory_structure, Status
from directory_info import DirectoryInfo, FileInfo
from Server.http_codes import *

def ProcessUploadRequest(data):
    try:
        UploadFile(data.get('path'), data)
        return {"status": AckCodes.OK.name}
    except FileExistsError:
        return {"status": AckCodes.FILE_ALREADY_EXISTS.name}
    except PathInvalidError:
        return {"status": AckCodes.FORBIDDEN.name}
    except UnauthorizedError:
        return {"status": AckCodes.UNAUTHORIZED.name}
    except ConflictError:
        return {"status": AckCodes.CONFLICT.name}
    except Exception:
        return {"status": AckCodes.CONFLICT.name}

def ProcessDownloadRequest(data):
    # Handle download requests, returning appropriate errors if conditions aren’t met
    path = data.get('path')
    owner = data.get('owner')
    status, file_content = DownloadFile(path, data)
    if status == AckCodes.OK:
        return {"status": status.name, "file_content": file_content}
    else:
        return {"status": status.name}

def ProcessDeleteRequest(data):
    # Call delete_file from FileIO.py, and check authorization and path validity
    path = data.get('path')
    result = DeleteFile(path, data)
    return {"status": result.name}

def ProcessDirRequest():
    # Return entire directory structure
    directory_structure = get_directory_structure()
    if directory_structure:
        return {"status": AckCodes.OK.name, "directory_structure": directory_structure}
    return {"status": AckCodes.NOT_FOUND.name}

def ProcessMoveRequest(data):
    # Change directories
    current_path = data.get('current_path')
    target_path = data.get('target_path')
    result = MoveDirectory(current_path, target_path, data)
    return {"status": result.name}

def ProcessModifyRequest(data):
    # Modify subdirectories
    path = data.get('path')
    subfolder_action = data.get('subfolder_action')
    result = ModifySubdirectories(path, subfolder_action, data)
    return {"status": result.name}

def ProcessSizeRequest(data):
    try:
        size = GetFileSize(data.get('path'), data)
        return {"status": AckCodes.OK.name, "size": size}
    except NotFoundError:
        return {"status": AckCodes.NOT_FOUND.name}
    except PathInvalidError:
        return {"status": AckCodes.FORBIDDEN.name}
    except UnauthorizedError:
        return {"status": AckCodes.UNAUTHORIZED.name}
    except ConflictError:
        return {"status": AckCodes.CONFLICT.name}
    except Exception:
        return {"status": AckCodes.CONFLICT.name}
