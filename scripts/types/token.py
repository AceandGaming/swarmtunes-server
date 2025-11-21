from dataclasses import dataclass, field
from typing import Optional, Callable, TYPE_CHECKING
from datetime import datetime
if TYPE_CHECKING:
    from scripts.types import User 

@dataclass
class Token:
    id: str
    userId: str
    secret: str #hashed
    expires: datetime

    def AddResolver(self, userResolver: Callable[[str], Optional["User"]]):
        self.userResolver = userResolver

    @property
    def user(self):
        if not hasattr(self, "userResolver"):
            print("Warning: Token does not have a user resolver")
            return None
        return self.userResolver(self.userId)
    
    @property
    def maxAge(self):
        return (self.expires - datetime.now()).total_seconds()