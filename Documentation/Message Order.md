# Message Order

This document describes the order in which messages are sent & processed.
For implementation details of these messages, please refer to the `Common/examples/format.md` file. 

## Connect

The client starts this message.
1. Client sends `connect`
2. Server will validate the request. It will send back an `ack` containing the status.

## Close

The client starts this message.
1. Client sends `close`
2. Server will validate the request. It will send back an `ack` containing the status.

## Ack

The server sends this message in response to another one.
1. Sever sends the `ack` based on a previous request.

## Size

The client or server can send this message. It changes the buffer size of the socket. 
1. The client or server sends the `size` message
2. The other end will set their buffer size to the new one
3. After the information sent right after the `size` message is received, the buffer size goes back to the agreed default.

## Delete

The client sends this message.
1. Client sends a `delete` message.
2. The server validates the request and sends back an `ack`.

## Dir

This one has two parts, request and response. The client starts this message.
1. Client sends a `dir` request message
2. Server sends a `size` message containing the size of the next `dir` response message
3. The server sends back a `dir` response message

## Download

This one has two parts, request and response. The client starts this message.
1. Client sends a `download` request message
2. Server sends a `download` response message. ***Note*** this message contains the buffer size needed to send the file, if it is a success
3. Server sends the targeted file

## Move

This is started with the client.
1. Client sends a `move` request
2. Server validates request and sends back an `ack`

## Subfolder

This is started with the client.
1. Client sends a `subfolder` request
2. Server validates request and sends back an `ack`.

## Upload

This is started with the client.
1. Client sends a `upload` request
2. Server validates request and sends back an `ack`.
3. If ok, client sends the file