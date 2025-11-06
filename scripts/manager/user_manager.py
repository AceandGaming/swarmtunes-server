from .manager import BaseManager
from scripts.database import UserDatabase
from scripts.types import User
from scripts.id_manager import IDManager

class UserManager(BaseManager[User]):
    def __init__(self):
        super().__init__(UserDatabase())
    
    def Create(self, **kwargs) -> User:
        id = IDManager.NewId(User)
        user = User(id=id, **kwargs)
        self.Save(user)
        return user