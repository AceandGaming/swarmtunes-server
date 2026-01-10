from dataclasses import dataclass, field
from typing import Optional, Callable, TYPE_CHECKING
from datetime import datetime
from .id_object import IDObject
if TYPE_CHECKING:
    from scripts.types import User 

@dataclass(eq=False)
class Token(IDObject):
    userId: str
    secret: str #hashed
    expires: datetime
    renewable: bool = field(default=False)

    def AddResolver(self, userResolver: Callable[[str], Optional["User"]]):
        self.userResolver = userResolver

    @property
    def user(self):
        if not hasattr(self, "userResolver"):
            raise Exception("Token does not have a user resolver")
        return self.userResolver(self.userId)
    
    @property
    def maxAge(self):
        return (self.expires - datetime.now()).total_seconds()