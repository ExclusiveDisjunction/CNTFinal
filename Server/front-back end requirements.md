# Front End and Back End Communication Requirements

This document outlines what the front end and back ends of the server require from each other.
It is separated by the kinds of messages.

## File System Note
All files from the server will be stored in some directory. That is up to implementation as to where this directory is. That directory will be called the `root` of the server file system. This is a 'virtual' file system. It is ***forbidden*** for users to request a path that leaves the root. For instance, if the user in `stuff`, and attempts to leave by moving to `../../`, this will be an invalid path. However, `../` is a valid path. In the system, the root is called "".

## Errors Note
If an operation fails, the back end should supply the front end with the reason as to why this happened. Ideally, we could make some exception classes. This is because the front end will send back HTTP status codes as to why the operation failed.

## Connect, Close, Ack, and Size Messages
These are soley front end messages, and have no merit on the back end. For the size command, the back end should be able to produce a file size, if requested. This is handled by the `FileInfo` class.

## Upload
The back end must:
1. Determine the validity of the path sent
    1. Is the path in valid format?
    2. Does the path attempt to leave the root?
    3. Does the file already exist?
2. Determine if the file can be uploaded
    1. Is it too large?

For the sake of the argument, if a file already exists (regardless of owner), it will fail. There is no file overriding. 

If all is correct, the front end will pass the data to place into the file. It will pass:
1. The name
2. The file's name
3. The kind
4. The owner
5. The current directory of the client

## Download
The client will request a download. It will pass a path. This path is relative to the current directory. The front end will pass:
1. The current directory
2. The current credentials
3. The path supplied by the client

It must determine if:
1. The path is valid (relative to the current directory)
    1. Does it try to leave the root?
    2. Does it point to a directory instead of a file?
    3. Does the current user own that file?

If all is correct, it will deliver the file to the front end. Otherwise, it will report the error.

## Delete
This will request that a file is removed. The front end will pass:
1. The path to modify
2. The credentials of the current user
3. The current directory of the user

The back end must determine:
1. If the path is valid?
    1. Does it try to leave the root?
    2. Does the file exist?
    3. Is it a folder, or a file?
    4. Does the current user own the rights to that file?

If this is sucessful, the back end should perform the action and tell the front end of its success. Otherwise, report the error.

## Dir
The back end must supply the entire directory structure as a `DirectoryInfo` instance tree. The front end will not pass any information to the back end

## Move
Requests that the current directory be changed. The front end will supply:
1. The current directory
2. The target directory path

The back end must determine:
1. Is the path valid (relative to the current directory)?
    1. Is it trying to leave the root?
    2. Is it a directory, or a file?
    3. Does the path exist?

## Subfolder
This will request that a directory is added or removed. The front end will pass:
1. The path to modify
2. The action. This will be in the form of a `SubfolderAction` enum instance
3. The current directory of the user

The back end must determine:
1. If the path is valid (relative to the current directory)?
    1. Does it try to leave the root?
    2. Does the folder exist?
    3. Is it a folder, or a file?

If this is sucessful, the back end should perform the action and tell the front end of its success. Otherwise, report the error.