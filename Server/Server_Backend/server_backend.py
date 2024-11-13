from file_io import UploadFile, DownloadFile, DeleteFile, MoveDirectory, ModifySubdirectories, ListFilesWrapper
from file_tracking import CheckFileOwner, GetDirectoryStructure, Status
from directory_info import DirectoryInfo, FileInfo
from ack_codes import AckCodes, GenerateAckMessage

def ProcessUploadRequest(data):
    # Validate and initiate file upload requests
    path = data.get('path')
    result = UploadFile(path, data)
    return {"status": result.name}

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
    directory_structure = GetDirectoryStructure()
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
