from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal
from abstract.id_object import IDObject
from datetime import datetime
from enum import Enum
if TYPE_CHECKING:
    from features import Playlist

class UserRoles(Enum):
    USER = "user"
    ADMIN = "admin"

#Temp
#TODO: Revisit once auth is implemented
@dataclass
class Auth:
    type: Literal["google", "discord", "legacy"]
    expires: datetime
    token: str

@dataclass(eq=False, kw_only=True)
class User(IDObject):
    username: str
    email: str
    auth: Auth
    playlists: list["Playlist"] = field(default_factory=list)
    role: UserRoles = UserRoles.USER

    @property
    def is_admin(self):
        return self.role == UserRoles.ADMIN