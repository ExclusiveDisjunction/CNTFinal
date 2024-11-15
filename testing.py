from Common.message_handler import *
from Server.io_tools import DirectoryInfo, FileInfo, FileType
from Server.credentials import Credentials
import socket

def client_dummy() -> bool:
    """
    A simple script to test the functionality of the server
    """

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 8080))
        data = s.recv(1024)
        print(data.decode("utf-8"))

        return True
    except:
        return False


def messages_tester() -> bool:
    """
    We will evaluate all kinds of messages. It will start by constructing an instance of that Message (request and response variants, if possible), and then sterilize into JSON. Then, it will de-sterilize, parse, and assert the two are equal.
    """

    messages = [
        (ConnectMessage("Hello", "Password"), True),
        (AckMessage(200, "OK"), False),
        (CloseMessage(), True),
        (UploadMessage("file", FileType.Text, 400), True),
        (DownloadMessage("file"), True),
        (DownloadMessage(200, "OK", FileType.Text, 400), False),
        (DeleteMessage("file"), True),
        (DirMessage(), True),
        (DirMessage(200, "OK", DirectoryInfo()), False),
        (MoveMessage("file"), True),
        (SubfolderMessage("directory", SubfolderAction.Add), True)
    ]

    try:
        for message, request in messages:
            sterilized = message.construct_message_json(request)
            result = MessageBasis.parse_from_json(sterilized)

            assert result == message
            print(f"Message {message.message_type().value} ({request}) passed")

    except Exception as e:
        print(f"Caught {str(e)}")

def dir_resp_test() -> bool:
    creds = "Hi"
    root = DirectoryInfo("", 
        [
            FileInfo("thing.wav", creds, FileType.Audio),
            FileInfo("thing2.wav", creds, FileType.Audio)
        ],
        [
            DirectoryInfo("one", 
            [
                FileInfo("thing.txt", creds, FileType.Text),
                FileInfo("thing2.txt", creds, FileType.Text)
            ],
            [
                DirectoryInfo("two")
            ])
        ])
    encoded = json.dumps(root.to_dict())
    print(encoded, end="\n\n")
    
    decoded = DirectoryInfo.from_dict(json.loads(encoded))
    assert root == decoded
    print("\nSucessfully decoded")


if __name__ == "__main__":
    if dir_resp_test():
        print("\nAll tests passed")
    else:
        print("\nOne or more tests failed")