from scripts.types import User
import secrets
from scripts.data_system import DataSystem
from datetime import datetime, timedelta

TOKEN_EXPIRATION_HOURS = 4

class SessionToken:
    def __init__(self, user: User):
        self.token = secrets.token_urlsafe(16)
        self.user = user
        self.date = datetime.now()
        self.expiration = self.date + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    def __repr__(self):
        return self.token
    def __eq__(self, other):
        if not isinstance(other, SessionToken) or not isinstance(self, SessionToken):
            return False
        return self.token == other.token

class SessionManager:
    tokens = []

    @staticmethod
    def AddToken(token: SessionToken):
        SessionManager.tokens.append(token)

    @staticmethod
    def RemoveToken(token: SessionToken):
        SessionManager.tokens.remove(token)

    @staticmethod
    def Login(username: str, password: str):
        user = DataSystem.users.GetUserFromLogin(username, password)
        if user is None:
            return None
        
        for token in SessionManager.tokens:
            if token.user == user:
                return token
            
        token = SessionToken(user)
        SessionManager.AddToken(token)
        return token

    @staticmethod
    def GetToken(user: User):
        for token in SessionManager.tokens:
            if token.user == user:
                return token
            
        token = SessionToken(user)
        SessionManager.AddToken(token)
        return token
    
    @staticmethod
    def Logout(tokenString: str):
        for token in SessionManager.tokens:
            if token.token == tokenString:
                SessionManager.RemoveToken(token)
                return
        
    @staticmethod
    def GetUser(tokenString: str):
        for token in SessionManager.tokens:
            if token.token == tokenString:
                return token.user
            
    @staticmethod
    def TokenIsValid(tokenString: str):
        for token in SessionManager.tokens:
            if token.token == tokenString:
                if token.expiration < datetime.now():
                    SessionManager.RemoveToken(token)
                    return False
                return True
        return False