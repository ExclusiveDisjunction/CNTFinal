from enum import Enum

class AckCodes(Enum):
    SEND_FILE = 100
    OK = 200
    FILE_ALREADY_EXISTS = 302
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    BUFFER_TOO_LARGE = 406
    CONFLICT = 409
    USER_NOT_SIGNED_IN = 503



def GenerateAckMessage(code):
    pass