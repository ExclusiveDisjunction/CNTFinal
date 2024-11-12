import os
from datetime import datetime

# Dictionary to store file metadata
file_metadata = {}

# Add or update file metadata
def add_file_metadata(file_path, owner, file_type):
    if os.path.exists(file_path):
        file_size = os.path.getsize(file_path)
        last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
        file_metadata[file_path] = {
            'owner': owner,
            'file_type': file_type,
            'size': file_size,
            'last_modified': last_modified
        }
        print(f"Metadata for '{file_path}' added/updated.")
    else:
        print(f"File '{file_path}' does not exist.")

# Get file metadata
def get_file_metadata(file_path):
    return file_metadata.get(file_path, "File metadata not found.")

# Remove file metadata
def remove_file_metadata(file_path):
    if file_path in file_metadata:
        del file_metadata[file_path]
        print(f"Metadata for '{file_path}' removed.")
    else:
        print(f"No metadata found for '{file_path}'.")

def get_file_info(file_path):
    """Return file metadata and content for front-end use."""
    metadata = get_file_metadata(file_path)
    if metadata:
        return {
            'status': 'success',
            'data': metadata
        }
    else:
        return {
            'status': 'error',
            'message': 'File metadata not found.'
        }