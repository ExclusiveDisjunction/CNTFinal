class Credentials:
    def __init__(self, username: str, passwordHash: str) -> None:

        self.__username = username
        self.__passwordHash = passwordHash

    def getUsername(self) -> str:
        return self.__username
    def getPasswordHash(self) -> str:
        return self.__passwordHash
    
    def __eq__(self, obj) -> bool:
        if self is None and obj is None:
            return True
        if self is None or obj is None:
            return False
        else:
            return self.__username == obj.__username and self.__passwordHash == obj.__passwordHash