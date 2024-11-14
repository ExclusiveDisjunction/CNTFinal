from file_tracking import get_file_owner
import mimetypes

class DirectoryInfo:
    def __init__(self, name, owner):
        self.kind = 'directory'
        self.name = name
        self.contents = []
        self.owner = owner

    def add_content(self, content):
        self.contents.append(content)

    def get_directory_owner(path):
        return get_file_owner(path)

class FileInfo:
    def __init__(self, name, file_type, owner, size):
        self.kind = 'file'
        self.name = name
        self.type = file_type
        self.owner = owner
        self.size = size

    def get_file_type(path):
        file_type, _ = mimetypes.guess_type(path)
        return file_type or 'unknown'
