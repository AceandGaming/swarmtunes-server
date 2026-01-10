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
import scripts.config as config

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
    
    def CreateFromUser(self, user: User, renewable: bool = False):
        secret = token_urlsafe(32)
        if renewable:
            expires = datetime.now() + timedelta(days=config.TOKEN_EXPIRATION_DAYS)
        else:
            expires = datetime.now() + timedelta(days=config.SESSION_EXPIRATION_HOURS)

        secretHash = sha256(secret.encode()).hexdigest()
        return self.Create(userId=user.id, secret=secretHash, expires=expires, renewable=renewable), secret
    
    def Refresh(self, token: Token):
        if not token.renewable:
            return token, None
        token.expires = datetime.now() + timedelta(days=config.TOKEN_EXPIRATION_DAYS)
        secret = token_urlsafe(32)
        token.secret = sha256(secret.encode()).hexdigest()
        self._database.Save(token)
        return token, secret
    
    def DeleteTokensOfUser(self, userId: str):
        for token in self.GetAll():
            if token.userId == userId:
                self.Remove(token)
    
    def HasExpired(self, token: Token):
        if token is None:
            return True
        return token.expires < datetime.now()
    
    def ValidateSecret(self, token: Token, secret: str):
        if token is None:
            return False
        if not hmac.compare_digest(token.secret, sha256(secret.encode()).hexdigest()):
            return False
        return True

    def ValidateToken(self, token: Token, secret: str):
        if token is None:
            return False
        if self.HasExpired(token):
            self.Remove(token)
            return False
        if UserManager().Get(token.userId) is None:
            self.DeleteTokensOfUser(token.userId)
            return False
        if not self.ValidateSecret(token, secret):
            self.DeleteTokensOfUser(token.userId)
            return False
        return True
    
    def RemoveId(self, id: str):
        token = self.Get(id)
        if token is None:
            return
        self.Remove(token)