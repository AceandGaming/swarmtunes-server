from scripts.classes.user import User
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Admin(User):
    @classmethod
    def CreateFromJson(cls, userJson: dict):
        user = super().CreateFromJson(userJson)
        if user is None:
            return
        user.adminHash = userJson["adminHash"]
        return user
    
    @property
    def isAdmin(self):
        return self.VerifyAdmin()

    def __init__(self, username: str, password: str):
        super().__init__(username, password)
        self.adminHash = pwd_context.hash(self.uuid) #prevents copy and pasting json
    def ToJson(self):
        playlistUUIDs = [playlist.uuid for playlist in self.playlists]
        return {
            "uuid": self.uuid,
            "username": self.username,
            "password": self.password,
            "playlists": playlistUUIDs,
            "adminHash": self.adminHash
        }
    def VerifyAdmin(self):
        return pwd_context.verify(self.uuid, self.adminHash)