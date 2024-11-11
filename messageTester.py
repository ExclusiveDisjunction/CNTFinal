from Common.message_handler import *

if __name__ == "__main__":
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