from .manager import BaseManager
from scripts.database import UserDatabase
from .playlist_manager import PlaylistManager
from scripts.types import User
from scripts.id_manager import IDManager
from passlib.context import CryptContext

context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserManager(BaseManager[User]):
    def __init__(self):
        super().__init__(UserDatabase())
    
    def Create(self, **kwargs) -> User:
        id = IDManager.NewId(User)
        user = User(id=id, **kwargs)
        self.Save(user)
        return user
    
    def UsernameExists(self, username: str):
        for user in self.items:
            if user.username == username:
                return True
        return False
    
    def CreateWithPassword(self, username: str, password: str):
        if self.UsernameExists(username):
            raise Exception("Username already taken")
        hash = context.hash(password)
        return self.Create(username=username, password=hash)
    
    def CheckPassword(self, user: User, password: str):
        return context.verify(password, user.password)
    
    def GetUserFromLogin(self, username: str, password: str):
        for user in self.items:
            if user.username == username:
                if self.CheckPassword(user, password):
                    return user
                break
        return None

    def Get(self, id: str):
        user = self._database.Get(id)
        if user is None:
            return None
        
        user.AddResolver(PlaylistManager().Get)
        return user