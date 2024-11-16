# exceptions.py

from enum import Enum
from .message_handler import AckMessage

class HttpCodes(Enum):
    Continue = 100
    Ok = 200
    Unauthorized = 401
    Forbidden = 403
    NotFound = 404
    TooLarge = 406
    Conflict = 409
    ImNotATeapot = 418

    def __int__(self):
        return self.value

class HTTPErrorBasis:
    """
    Represents an error that can be converted to an ACK message.
    """

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message

    def to_ack(self) -> AckMessage:
        return AckMessage(self.code, self.message)
    
class ImNotATeapotError(HTTPErrorBasis):
    def __init__(self, reason: str):
        super().__init__(HttpCodes.ImNotATeapot, reason)

class UnauthorizedError(HTTPErrorBasis):
    def __init__(self, reason: str = "Not signed in"):
        super().__init__(HttpCodes.Unauthorized, reason)

class ForbiddenError(HTTPErrorBasis):
    def __init__(self):
        super().__init__(HttpCodes.Forbidden, "Path leaves the storage area")

class NotFoundError(HTTPErrorBasis):
    def __init__(self):
        super().__init__(HttpCodes.NotFound, "Path not found, or points to the wrong resource")

class BufferSizeTooLargeError(HTTPErrorBasis):
    def __init__(self):
        super().__init__(HttpCodes.TooLarge, "File size is too large")

class ConflictError(HTTPErrorBasis):
    def __init__(self, reason: str):
        super().__init__(HttpCodes.Conflict, reason)

