from abstract.id_object import SQLIDObject
from sqlalchemy import String, JSON, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING, TypedDict, Literal
from features.user.user import UserRoles
if TYPE_CHECKING:
    from .playlist import SQLPlaylist

class Auth(TypedDict):
    type: Literal["google", "discord", "legacy"]
    expires: str
    token: str

class SQLUser(SQLIDObject):
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    auth: Mapped[Auth] = mapped_column(JSON, nullable=False)
    playlists: Mapped[list["SQLPlaylist"]] = relationship("SQLPlaylist", back_populates="user")
    role: Mapped[UserRoles] = mapped_column(Enum, nullable=False, default=UserRoles.USER)
