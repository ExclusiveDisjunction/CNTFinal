from pathlib import Path
import os
from enum import Enum
from math import ceil
from socket import socket
from typing import Self

file_buffer_size = 4096

class FileType(Enum):
    Text = "text"
    Audio = "audio"
    Video = "video"

def get_file_type(path: Path) -> FileType | None:
    if path is None:
        return None
    
    match path.suffix:
        case ".mp4" | ".mov" | ".avi" | ".wmv":
            return FileType.Video
        case ".mp3" | ".wav" | ".aac" | ".flac" | ".aiff":
            return FileType.Audio
        case _:
            return FileType.Text
        
def get_file_total_size(path: Path | str) -> int | None:
    if path is None:
        return None
    
    if isinstance(path, str):
        path = Path(path)
    
    if not path.is_file():
        return None
    
    try:
        return os.path.getsize(path)
    except:
        return None

class FileInfo:
    """
    A structure that contains the path & allows for relative moving
    """

    def __init__(self, name: str | str, owner_username, kind: FileType, size: int, parent = None):
        self.__parent = parent
        self.__name = name
        self.__owner = owner_username
        self.__kind = kind

    def to_dict(self) -> dict:
        return {
            "kind": "file",
            "name": self.__name,
            "file_kind": self.__kind.value,
            "owner": self.__owner
        }
    def from_dict(data: dict, parent = None) -> Self:
        try:
            name = data["name"]
            file_kind = FileType(data["file_kind"])
            owner = data["owner"]
        except:
            name = None
            file_kind = None
            owner = None

        if name == None or file_kind == None:
            raise ValueError("The dictionary does not contain enough data to fill this structure")
        
        return FileInfo(name, owner, file_kind, parent)
          
    def __eq__(self, other) -> bool:
        if self is None and other is None:
            return True
        elif self is None or other is None:
            return False
        
        return self.__name == other.__name and self.__owner == other.__owner and self.__kind == other.__kind
    
    def name(self) -> str:
        return self.__name
    def kind(self) -> FileType:
        return self.__kind
    def owner_username(self) -> str:
        return self.__owner
    def parent(self):
        return self.__parent
    def set_parent(self, parent):
        self.__parent = parent
    
    def target_path_relative(self) -> Path:
        """
        Returns the current path relative to the root
        """

        if self.__parent is None:
            return None
        
        return self.__parent.target_path_relative().joinpath(self.__name)
    
    def target_path_absolute(self, env_path: Path) -> str:
        """
        Returns the current path relative to the OS root
        """
        return env_path.joinpath(self.target_path_relative())

class DirectoryInfo:
    def __init__(self, name: str, contents: list[FileInfo | Self] | None = None, parent: Self | None = None):
        self.__name = name
        if contents is None:
            self.__contents = []
        else:
            self.__contents = contents

        self.__parent = parent

        # Build proper order
        for content in self.__contents:
            if content is not None:
                content.set_parent(self)

    def to_dict(self) -> dict:
        contents = []
        for item in self.__contents:
            contents.append(item.to_dict())
        return {
            "kind": "directory",
            "name": self.__name,
            "contents": contents
        } 
    def from_dict(data: dict) -> Self | None:
        try:
            name = data["name"]
            contents = list(data["contents"])
        except:
            name = None
            contents = None
        
        if name == None or contents == None:
            raise ValueError("The contents could not be read")
        
        trueContents = []
        for info in contents:
            if info["kind"] == "directory":
                trueContents.append(DirectoryInfo.from_dict(info))
            elif info["kind"] == "file":
                trueContents.append(FileInfo.from_dict(info))

        return DirectoryInfo(name, trueContents)
    
    def __eq__(self, other) -> bool:
        if other is None and self is None:
            return True
        elif other is None or self is None:
            return False
        else:
            return self.__name == other.__name and self.__files == other.__files and self.__dirs == other.__dirs
        
    def name(self) -> str:
        return self.__name
    def parent(self) -> Self | None:
        return self.__parent
    def set_parent(self, parent: Self | None):
        self.__parent = parent

    def target_path_relative(self) -> Path:
        """
        Returns the current path relative to the root
        """

        if self.__parent is None:
            return Path("")
        else:
            return self.__parent.target_path_relative().joinpath(self.__name)
    
    def target_path_absolute(self, env_path: Path) -> str:
        """
        Returns the current path relative to the OS root
        """
        return env_path.joinpath(self.target_path_relative())
        
    def add_content(self, content):
        self.__contents.append(content)
    def contents(self):
        return self.__contents
    def set_contents(self, contents: list[Self | FileInfo] | None):
        if contents is None:
            self.__contents = []
        else:
            self.__contents = contents

def read_file_for_network(path: Path, buff_size: int = file_buffer_size) -> list[bytes] | None:
    """
    Reads the contents of a file as binary, and then splits it up into buff_size chunks
    """
    try:
        f = open(path, 'rb')

        contents = f.read()
        f.close()

        return split_binary_for_network(contents, buff_size)
    except:
        return None
    
def split_binary_for_network(contents: bytes, buff_size: int = file_buffer_size) -> list[bytes] | None:
    """
    Splits a binary input into a series of buff_size chunks
    """
    if contents is None:
        return None
    
    result = list([contents[i * buff_size:(i+1) * buff_size] for i in range(int(ceil(len(contents) / buff_size))) ])
    if len(result) != 0:
        result[-1] = result[-1].ljust(4096, b'\x00') # We have to add trailing zeroes so that our data will always fit within the buffer & the recv will work properly

    avg_size = 0
    for item in result:
        avg_size += len(item) / len(result)

    return result
    
def receive_network_file(path: Path, s: socket, frame_size: int, buff_size: int = file_buffer_size) -> bool:
    """
    Constructs the file sent over a network, assuming said file was sent using the split_binary_for_network protocol
    """
    retry_count = 5
    try:
        if frame_size < 0:
            return False
        
        total_windows = frame_size
        frame_size *= buff_size
        windows_so_far = 0.0
        
        with open(path, 'wb') as f:
            while frame_size > 0 and windows_so_far < total_windows:
                try:
                    chunk = s.recv(buff_size)
                    if chunk is None or len(chunk) == 0:
                        print("[DEBUG] Network Rev Finished, chunks not all done.")
                        return False
                    
                    if frame_size <= buff_size: # Last packet
                        f.write(chunk.rstrip(b'\x00')) # Remove trailing zeroes from buffer packing
                    else:
                        f.write(chunk)

                    frame_size -= len(chunk)
                    windows_so_far += len(chunk) / buff_size
                except socket.timeout:
                    if retry_count <= 0:
                        print(f"[IO] Network file recv failed because of retry fails")
                        return False
                    retry_count -= 1
                    continue

        return True
    except Exception as e:
        print(f"[IO] Network file recv failed with message '{str(e)}'")
        return False
def receive_network_file_binary(socket: socket, frame_size: int, buff_size: int = file_buffer_size) -> bytes | None:
    """
    Constructs the file sent over a network, assuming said file was sent using the split_binary_for_network protocol
    """
    retry_count = 5
    try:
        if frame_size < 0:
            return None
        
        total_windows = frame_size
        frame_size *= buff_size
        windows_so_far = 0.0

        result = b''
        while frame_size > 0 and windows_so_far < total_windows:
            try:
                chunk = socket.recv(buff_size)
                if chunk is None or len(chunk) == 0:
                    print("[DEBUG] Network Rev Finished, chunks not all done.")
                    return None
            
                if frame_size <= buff_size: # Last packet
                    result += chunk.rstrip(b'\x00') # Remove trailing zeroes from buffer packing
                else:
                    result += chunk

                frame_size -= len(chunk)
                windows_so_far += len(chunk) / buff_size
            except socket.timeout:
                if retry_count <= 0:
                    print(f"[IO] Network file recv failed because of retry fails")
                    return None
                retry_count -= 1
                continue

        return result
    except Exception as e:
        print(f"[IO] Network file recv failed with message '{str(e)}'")
        return None