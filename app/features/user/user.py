from abstract.id_object import IDObject
from sqlalchemy import String, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING, Optional
from enum import Enum
if TYPE_CHECKING:
    from features.playlist.playlist import Playlist
    from features.identity.identity import Identity
    from features.session.token import Token

class UserRoles(Enum):
    USER = "user"
    ADMIN = "admin"

class User(IDObject):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column()
    email: Mapped[Optional[str]] = mapped_column(unique=True)

    role: Mapped[UserRoles] = mapped_column(SQLAlchemyEnum(UserRoles), default=UserRoles.USER)

    playlists: Mapped[list["Playlist"]] = relationship(
        "Playlist",
        back_populates="user"
    )
    tokens: Mapped[list["Token"]] = relationship(
        "Token",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    identities: Mapped[list["Identity"]] = relationship(
        "Identity",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
