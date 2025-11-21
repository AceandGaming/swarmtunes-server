from .manager import BaseManager
from scripts.database import TokenDatabase
from .user_manager import UserManager
from scripts.types import User
from scripts.id_manager import IDManager
from secrets import token_urlsafe
from scripts.types import Token
from datetime import datetime, timedelta
from hashlib import sha256
import hmac

TOKEN_MAX_EXPIRATION_DAYS = 30

class TokenManager(BaseManager[Token]):
    def __init__(self):
        super().__init__(TokenDatabase())

    def Create(self, **kwargs) -> Token:
        """Note: Provided secret is NOT hashed!"""
        id = IDManager.NewId(Token)
        token = Token(id=id, **kwargs)
        self.Save(token)
        return token
    
    def Get(self, id: str):
        token = self._database.Get(id)
        if token is None:
            return None
        token.AddResolver(UserManager().Get)
        return token
    
    def CreateFromUser(self, user: User):
        secret = token_urlsafe(32)
        expires = datetime.now() + timedelta(days=TOKEN_MAX_EXPIRATION_DAYS)
        secretHash = sha256(secret.encode()).hexdigest()
        return self.Create(userId=user.id, secret=secretHash, expires=expires), secret
    
    def Refresh(self, token: Token):
        token.expires = datetime.now() + timedelta(days=TOKEN_MAX_EXPIRATION_DAYS)
        secret = token_urlsafe(32)
        token.secret = sha256(secret.encode()).hexdigest()
        self._database.Save(token)
        return token, secret
    
    def DeleteTokensOfUser(self, userId: str):
        for token in self.GetAll():
            if token.userId == userId:
                self.Remove(token)
    
    def HasExpired(self, id: str):
        token = self.Get(id)
        if token is None:
            return True
        return token.expires < datetime.now()
    
    def GetWithSecret(self, id: str, secret: str):
        token = self.Get(id)
        if token is None:
            return None
        if not hmac.compare_digest(token.secret, sha256(secret.encode()).hexdigest()):
            return None
        return token

    def Validate(self, id: str, secret: str):
        token = self.Get(id)
        if token is None:
            return None
        if token.expires < datetime.now():
            return None
        if UserManager().Get(token.userId) is None:
            self.DeleteTokensOfUser(token.userId)
            return None
        if not hmac.compare_digest(token.secret, sha256(secret.encode()).hexdigest()):
            self.DeleteTokensOfUser(token.userId)
            return None
        return token
    
    def RemoveId(self, id: str):
        token = self.Get(id)
        if token is None:
            return
        self.Remove(token)