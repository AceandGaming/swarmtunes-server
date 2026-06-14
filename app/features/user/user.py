from abstract.id_object import IDObject
from sqlalchemy import String, JSON, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING, TypedDict, Literal
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
if TYPE_CHECKING:
    from ..playlist.playlist import Playlist


class UserRoles(Enum):
    USER = "user"
    ADMIN = "admin"

#Temp
#TODO: Revisit once auth is implemented
@dataclass
class Auth:
    type: Literal["google", "discord", "legacy"]
    expires: datetime

class User(IDObject):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)

    role: Mapped[UserRoles] = mapped_column(SQLAlchemyEnum(UserRoles), default=UserRoles.USER)
    auth: Mapped[Auth] = mapped_column(JSON)

    playlists: Mapped[list["Playlist"]] = relationship(
        back_populates="user"
    )
