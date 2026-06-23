from abstract.id_object import IDObject
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import Enum as SQLAlchemyEnum
from database.relationships import album_songs
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum
from features.collection import Collection
if TYPE_CHECKING:
    from features.song import Song

class AlbumType(Enum):
    SETLIST = "setlist"

class Album(IDObject, Collection):
    __tablename__ = "playlists"

    title: Mapped[str] = mapped_column()
    type: Mapped[AlbumType] = mapped_column(SQLAlchemyEnum(AlbumType))

    custom_artwork: Mapped[Optional[str]] = mapped_column()
    date: Mapped[Optional[datetime]] = mapped_column()

    songs: Mapped[list["Song"]] = relationship(
        "Song",
        secondary=album_songs,
        back_populates="playlists"
    )

