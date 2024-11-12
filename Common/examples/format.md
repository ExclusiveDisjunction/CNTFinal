# JSON Message Format Guide

## All Commands
The JSON text must contain three sections:
1. Convention: The Command used
2. Direction: If it is comming from the client or the server. request if from client, response if from server
3. Data: The section containing the message information

## Connect
The connect file is used to send the user's credential information to the server. The length of this file cannot exceede 1024 bytes. The data section must contain:
1. Username -> String
2. Password -> Hashed String containing user's password

Upon receiving this, the server will send back an `ack` message. If it returns 202, then the user is signed in. Otherwise, if 401 (unauthorized) is returned, then the user's info was incorrect.

## Close
The close file is used to tell the server to clear out this session and disconnect from the session. 

The server will respond with `ack`:
1. 200: User signed out sucessfully. (Given that the user is signed in)
2. 503: User is not currently signed in

## Ack
The ack, or acknoledgement command, is used by the server to send a quick message back to the client. It contains:
1. Code: The code using HTTP code guidelines
2. Reason: A string containing the reason why the code was sent. 

***Note***: If the client requests something that the server does not know how to futfil, it will return 418 (I'm a teapot)

## Size
Inform either the client or server that the message about to be sent is of a specified size, and to change the buffer size.
It contains:
1. `size`: The number of bytes about to be sent.

This message is followed up with the information about to be sent. It is a bi-directional message

## Move
Request that the directory be changed. The client must provide a relative path to move to. The direction is only `request`.
The data section must contain:
1. `path`: The relative path to move to

The server will send an `ack` in response:
1. 200: Moved successfully
2. 401: Unauthorized (not signed in)
3. 403: Forbidden (path attempting to leave root)
4. 404: Not found (Path not found in index)

## Delete
Request that the provided path is deleted. The client must provide a relative path to move to. The direction is only `request`. 

The data section must contain:
1. `path`: The relative path to remove

The server will send an `ack` in response:
1. 200: Deleted successfully
2. 401: Unauthorized (not signed in)
3. 403: Forbidden (path attempting to leave root)
4. 404: Not found (Path not found in index)

## Upload
Submit a request to upload a file. The direction is only `request`.

The data section must contain:
1. `name`: File name
2. `kind`: Either `audio`, `video`, or `text`.
3. `size`: The size of the file, in bytes. 

The upload will respond with an `ack`:
1. 100: Send file
2. 302: File already exists
3. 401: Unauthorized (not signed in, or file owned by another user)
4. 403: Forbidden (path attempting to leave root)
5. 404: Not found (Path not found in index)
6. 406: Buffer size too large

After the `ack` has been sent, the server expects the client to send the information. It will wait until the user sends all of the file promised. Once received, it will send another `ack`:
1. 200: OK

## Download

### Request
Request that a file on the server get sent to the client.

The data section must contain:
1. `path`: Relative path to file

The server will return a `download response` message.

### Response 
A response to the client sending a `download request`. 

The data section must contain:
1. `status`: A code containing the status of the request
    1. 200: Ok
    2. 401: Unauthorized (not signed in, or not owned by current user)
    3. 403: Forbidden (path attempting to leave root)
    4. 404: Not found (path not found in index)
2. `message`: A string containing the message from the `status`
3. `format`: Can either be empty (error status), or contain:
    1. `kind`: The kind of file. Either `text`, `video`, or `audio`
    2. `size`: The size of the file, in bytes

## Dir
### Request
Requests the directory structure from the server.
The data section contains no elements.

The server will respond with a `dir response` message

### Response
A response to the `dir request` message.

The data section consists of:
1. `response`: The response code
    1. 200: Ok
    2. 401: Unauthorized (not signed in)
2. `message`: The response message
3. `curr_dir`: The current directory of the client
3. `root`: The begining of the directory structure.
    1. This contains a specific format that is recursive to denote all files and folders. 

The format for directories and files goes as follows:

1. `kind`: Either `directory` or `file`. 
2. `name`: The name of the resource
3. `contents`: A list containing this format
4. `owner`: The owner of the resource. For directories, this is `server`. 

Note that the first entry in the data is the `root` directory.

## Subfolder
Request to add or remove a subfolder. The direction is only `request`.

The data section must contain:
1. `path`: The relative path to the folder to remove or add
2. `action`: Either `delete` or `add`. Signals what to do.

The server will send back an `ack`:
1. 200: OK
2. 401: Unauthorized (not signed in)
3. 403: Forbidden (path attempting to leave root)
4. 404: Not found (path not found in index)
5. 409: Conflict (path already exists)
