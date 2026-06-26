from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abstract.id_object import IDObject
from database.relationships import album_songs
from database.types import UTCDateTime

if TYPE_CHECKING:
    from features.song import Song


class AlbumType(Enum):
    SETLIST = "setlist"


class Album(IDObject):
    __tablename__ = "albums"

    title: Mapped[str]
    type: Mapped[AlbumType] = mapped_column(SQLAlchemyEnum(AlbumType))

    custom_artwork: Mapped[Optional[str]]
    date: Mapped[Optional[datetime]] = mapped_column(UTCDateTime())

    songs: Mapped[list["Song"]] = relationship(
        "Song", secondary=album_songs, back_populates="albums"
    )
