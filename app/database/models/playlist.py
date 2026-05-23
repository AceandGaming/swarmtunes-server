from abstract.id_object import SQLIDObject
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from .relationships import playlist_songs

if TYPE_CHECKING:
    from .song import SQLSong


class SQLPlaylist(SQLIDObject):
    __tablename__ = "playlists"

    title: Mapped[str] = mapped_column(String, nullable=False)
    artwork: Mapped[str] = mapped_column(String, nullable=True)
    songs: Mapped[list[SQLSong]] = relationship(
        "SQLSong",
        secondary=playlist_songs,
        back_populates="playlists"
    )
    protected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)