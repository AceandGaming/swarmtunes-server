from scripts.classes.user import UserManager, User
import secrets

class SessionToken:
    def __init__(self, user: User):
        self.token = secrets.token_urlsafe(16)
        self.user = user
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
        user = UserManager.GetUserWithUsername(username)
        if user is None:
            return None
        if not user.VerifyPassword(password):
            return None
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
        return SessionManager.GetUser(tokenString) is not None