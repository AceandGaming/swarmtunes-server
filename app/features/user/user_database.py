from .database import BaseDatabase
import scripts.paths as paths
from scripts.serializer import UserSerializer
from scripts.types import User

class UserDatabase(BaseDatabase[User]):
    def __init__(self):
        super().__init__(User, UserSerializer, paths.USERS_DIR)