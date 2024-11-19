from pathlib import Path
import os

def make_file_sendable(path: Path, buffer_size: int) -> bytes | None:
    try:
        f = open(path, 'rb')

        contents = f.read()
        contents += b'\r\n'

        f.close()

        return contents

    except:
        return None
    
def recv_file(buffer: bytes) -> tuple[bytes, bool]: # The contents recv, true if continuing
    buffer = buffer.strip(b'\0')

    if buffer.endswith(b'\r\n'):
        buffer = buffer.removesuffix(b'\r\n')
        return buffer, False
    else:
        return buffer, True