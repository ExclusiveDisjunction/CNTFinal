class FileSystemError(Exception):
    """Base class for file system exceptions."""
    pass

class PathInvalidError(FileSystemError):
    pass

class UnauthorizedError(FileSystemError):
    pass

class NotFoundError(FileSystemError):
    pass

class ConflictError(FileSystemError):
    pass

class FileExistsError(FileSystemError):
    pass

class BufferTooLargeError(FileSystemError):
    pass
