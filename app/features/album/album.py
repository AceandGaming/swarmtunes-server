from datetime import datetime, timezone
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abstract.id_object import IDObject
from database.relationships import album_songs
from database.types import StringValueEnum, UTCDateTime

if TYPE_CHECKING:
    from features.song import Song


class AlbumType(StrEnum):
    DATE_SETLIST = "setlist"
    DISC_COLLECTION = "collection"


class Album(IDObject):
    __tablename__ = "albums"

    title: Mapped[str]
    custom_artwork: Mapped[Optional[str]]
    last_updated: Mapped[datetime] = mapped_column(
        UTCDateTime(), default=datetime.now(timezone.utc)
    )

    type: Mapped[AlbumType] = mapped_column(StringValueEnum(AlbumType))
    date: Mapped[Optional[datetime]] = mapped_column(UTCDateTime())
    disc: Mapped[Optional[int]]

    songs: Mapped[list["Song"]] = relationship(
        "Song", secondary=album_songs, back_populates="albums"
    )

    __table_args__ = (
        CheckConstraint(
            """
                (type = 'collection' AND disc IS NOT NULL) OR
                (type = 'setlist' AND date IS NOT NULL)
            """,
            name="ck_albums_vaild_type_data",
        ),
        Index("ix_album_type_date", "type", "date"),
        Index("ix_album_type_disc", "type", "disc"),
    )
