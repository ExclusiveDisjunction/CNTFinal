import os

def write_file(file_path, data):
    try:
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"File '{file_path}' written successfully.")
    except Exception as e:
        print(f"Error writing file '{file_path}': {e}")

def read_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            data = file.read()
        print(f"File '{file_path}' read successfully.")
        return data
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        return None

def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"Error deleting file '{file_path}': {e}")