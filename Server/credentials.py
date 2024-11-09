class Credentials:
    def __init__(self, username: str, passwordHash: str) -> None:
        if len(username) == 0 or len(passwordHash) == 0:
            raise SyntaxError("The username or password has were empty") 

        self.__username = username
        self.__passwordHash = passwordHash

    def getUsername(self) -> str:
        return self.__username
    def getPasswordHash(self) -> str:
        return self.__passwordHash
    
    def __eq__(self, obj) -> bool:
        return self.__username == obj.__username and self.__passwordHash == obj.__passwordHash