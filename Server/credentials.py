from pathlib import Path
import json

from .server_paths import user_database_loc

class Credentials:
    def __init__(self, username: str, passwordHash: str):

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
        
class UserDatabase:
    def __init__(self):
        self.__path = None
        self.__users = None
        
    def open(self, path: Path):
        if path is None:
            raise ValueError("Path must not be none")
        
        if not path.exists():
            try:
                path.touch()
            except:
                raise ValueError("Path could not be created")
        
        self.__path = path
        with open(self.__path, "r") as f:
            contents = f.read()
            if contents is None or len(contents) == 0:
                contents = "{ }"

            self.__users = dict(json.loads(contents))
        
        if self.__users is None:
            raise ValueError("Could not load database from that path")

    def get_user(self, username: str) -> None | Credentials:
        if not isinstance(username, str):
            username = str(username)

        if username in self.__users:
            return Credentials(username, self.__users[username])
        else:
            return None
        
    def set_user_pass(self, cred: Credentials) -> Credentials:
        self.__users[cred.getUsername()] = cred.getPasswordHash()

    def save(self):
        with open(self.__path, "w") as f:
            contents = json.dumps(self.__users)
            f.write(contents)

user_database = UserDatabase()