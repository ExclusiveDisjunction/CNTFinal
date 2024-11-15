1. Make it so that usernames and passwords are validated in the IO model. There should be a file somewhere containing the runtime information for users
2. If a connection request contains a username that is not known, add it. 
3. If the IO model does not validate the username and password pair, close the connection.