from abstract.id_object import IDObject
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import Enum as SQLAlchemyEnum
from database.relationships import album_songs
from database.types import UTCDateTime
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
if TYPE_CHECKING:
    from features.song import Song

class AlbumType(Enum):
    SETLIST = "setlist"

class Album(IDObject):
    __tablename__ = "albums"

    title: Mapped[str] = mapped_column()
    type: Mapped[AlbumType] = mapped_column(SQLAlchemyEnum(AlbumType))

    custom_artwork: Mapped[Optional[str]] = mapped_column()
    date: Mapped[Optional[datetime]] = mapped_column(UTCDateTime())

    songs: Mapped[list["Song"]] = relationship(
        "Song",
        secondary=album_songs,
        back_populates="albums"
    )

