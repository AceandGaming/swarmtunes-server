from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abstract.id_object import IDObject

if TYPE_CHECKING:
    from features.identity.identity import Identity
    from features.playlist.playlist import Playlist
    from features.session.token import Token


class UserRoles(Enum):
    USER = "user"
    ADMIN = "admin"


class User(IDObject):
    __tablename__ = "users"

    username: Mapped[str]
    email: Mapped[Optional[str]] = mapped_column(unique=True)

    role: Mapped[UserRoles] = mapped_column(
        SQLAlchemyEnum(UserRoles), default=UserRoles.USER
    )

    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist", back_populates="user"
    )
    tokens: Mapped[list["Token"]] = relationship(
        "Token", back_populates="user", cascade="all, delete-orphan"
    )
    identities: Mapped[list["Identity"]] = relationship(
        "Identity", back_populates="user", cascade="all, delete-orphan"
    )
