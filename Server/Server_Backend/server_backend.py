from file_io import store_file, read_file, delete_file
from file_manager import add_file_metadata, get_file_metadata
from auth import authenticate

def handle_upload(username, file_path, file_data):
    # Check if the user is authenticated and has access
    store_file(file_path, file_data)
    add_file_metadata(file_path, username, "file type here")
    return "File uploaded successfully."

def handle_download(username, file_path):
    # Check ownership
    metadata = get_file_metadata(file_path)
    if metadata["owner"] != username:
        return "BAD ACCESS"
    return read_file(file_path)
