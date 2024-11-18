from Common.message_handler import *
from Server.io_tools import DirectoryInfo, FileInfo, FileType, get_file_size
import socket

def print_dir_structure(dir: DirectoryInfo, ts = ''):
    if dir is None:
        return
    
    print(f"{ts}{dir.name()} (d)")
    for item in dir.contents():
        if isinstance(item, FileInfo):
            print(f"{ts+'\t'}{item.name()} (f)")
        else:
            print_dir_structure(item, ts + '\t')

def client_dummy() -> bool:
    """
    A simple script to test the functionality of the server
    """

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("127.0.0.1", 8081))
        
        connect = ConnectMessage("hi", "djdlkdjf")
        s.sendall(connect.construct_message_json().encode())

        contents = s.recv(1024)
        if contents is None or len(contents) == 0:
            print("Connection terminated")
            s.close()

            return False

        recv = MessageBasis.parse_from_json(contents.decode("utf-8"))
        if not isinstance(recv, AckMessage):
            print(f"Unexpected message of type {recv.message_type()}")
            s.close()
            return False
        
        print("Requesting dir structure")
        s.sendall(DirMessage().construct_message_json().encode())
        contents = MessageBasis.parse_from_json(s.recv(1024).decode("utf-8"))
        size = contents.size()
        contents = MessageBasis.parse_from_json(s.recv(size).decode("utf-8"))
        print_dir_structure(contents.root())
        
        print("Closing connection")
        s.send(CloseMessage().construct_message_json().encode())

        contents = s.recv(1024)
        if contents is None or len(contents) == 0:
            print("Connection terminated")
            s.close()

            return False

        recv = MessageBasis.parse_from_json(contents.decode("utf-8"))
        if not isinstance(recv, AckMessage):
            print(f"Unexpected message of type {recv.message_type()}")
            s.close()
            return False

        return True
    except Exception as e:
        print(f"Caught {str(e)}")
        return False

def client_test_server() -> bool:
    try:
        ip = input("What is the server IP? (0 for local host, -1 for server external) ")
        port = input("What is the port? (0 for default) ")
        if ip == 0:
            ip = "127.0.0.1"
        elif ip == -1:
            ip = "35.184.69.189"
        if port == 0:
            port = 61324


        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        
        connect = ConnectMessage("hi", "djdlkdjf")
        s.sendall(connect.construct_message_json().encode())

        contents = s.recv(1024)
        if contents is None or len(contents) == 0:
            print("Connection terminated")
            s.close()

            return False

        recv = MessageBasis.parse_from_json(contents.decode("utf-8"))
        if not isinstance(recv, AckMessage):
            print(f"Unexpected message of type {recv.message_type()}")
            s.close()
            return False
        
        def get_contents(socket, size: int = 1024):
            return socket.recv(size).strip(b'\x00').decode("utf-8")
        def get_message(socket, size: int = 1024):
            return MessageBasis.parse_from_json(get_contents(socket, size))
        def send_message(socket, message: MessageBasis):
            socket.send(message.construct_message_json().encode())

        send_message(s, UploadMessage(Path("test.txt"), FileType.Text, get_file_size("test.txt")))
        ack = get_message(s)
        if ack is not None and isinstance(ack, AckMessage):
            if ack.code() != 200:
                print(f"Upload failed because '{ack.message()}'")
            else:
                with open(Path("test.txt").resolve(), 'r') as f:
                    contents = f.read()
                
                s.sendall(contents.encode())

                ack = get_message(s)
                if ack is not None and isinstance(ack, AckMessage):
                    if ack.code() != 200:
                        print(f"Upload failed because '{ack.message()}'")
                    else:
                        print("Upload success")
        
        send_message(s, DownloadMessage("thingone.txt"))
        download_resp = get_message(s)
        if download_resp is not None and isinstance(download_resp, DownloadMessage):
            if download_resp.status() == 200:
                print("Downloading file")
                size = download_resp.size()
                contents = get_contents(s, size)
                with open(Path("testone.txt").resolve(), 'w') as f:
                    f.write(contents)
                
                print("Download success")
            else:
                print(f"Download failed because of reason: {download_resp.message()}")
        

        send_message(s, DeleteMessage("thingone.txt"))
        ack = get_message(s)
        if ack is not None and isinstance(ack, AckMessage):
            if ack.code() == 200:
                print("Deleted file success")
            else:
                print(f"Failed to delete because '{ack.message()}'")

        send_message(s, DirMessage())
        size_message = get_message(s)
        dir_resp = get_message(s, size_message.size())
        if dir_resp is not None and isinstance(dir_resp, DirMessage):
            if dir_resp.code() == 200:
                print("Directory structure:\n")
                print_dir_structure(dir_resp.root())
                print("")
            else:
                print(f"Failed to get directory structure because: {dir_resp.message()}")

        send_message(s, MoveMessage("dir_one"))
        ack = get_message(s)
        if ack is not None and isinstance(ack, AckMessage):
            if ack.code() == 200:
                print("Moved successful")
            else:
                print(f"Could not move because of '{ack.message()}'")
        
        send_message(s, SubfolderMessage("dir_two", SubfolderAction.Add))
        ack = get_message(s)
        if ack is not None and isinstance(ack, AckMessage):
            if ack.code() == 200:
                print("Subfolder add successful")
            else:
                print(f"Could not add subdirectory because of '{ack.message()}'")
        
        
        print("Closing connection")
        s.send(CloseMessage().construct_message_json().encode())
        s.close()

        return True
    except Exception as e:
        print(f"Caught {str(e)}")
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
    if client_test_server():
        print("\nAll tests passed")
    else:
        print("\nOne or more tests failed")