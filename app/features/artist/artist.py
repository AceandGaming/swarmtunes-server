from typing import TYPE_CHECKING, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base
from database.relationships import song_artists, song_singers

if TYPE_CHECKING:
    from features.song import Song


class Artist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    original_name: Mapped[Optional[str]] = mapped_column(String)

    songs_artist: Mapped[list["Song"]] = relationship(
        secondary=song_artists, back_populates="artists"
    )

    songs_singer: Mapped[list["Song"]] = relationship(
        secondary=song_singers, back_populates="singers"
    )
