from abstract.id_object import SQLIDObject
from sqlalchemy import String, Integer, Boolean, Float, DateTime, JSON, Enum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from typing import Literal, Optional, TypedDict, TYPE_CHECKING
from .relationships import song_artists, song_singers, playlist_songs
from .artist import SQLArtist
from features.song.song import SongType, SongMetadataSource

if TYPE_CHECKING:
    from .playlist import SQLPlaylist

class AudioReference(TypedDict):
    type: Literal["gdrive", "youtube", "audio"]
    id: str

class SQLSong(SQLIDObject):
    __tablename__ = "songs"

    title: Mapped[str] = mapped_column(String, nullable=False)
    title_original: Mapped[Optional[str]] = mapped_column(String)

    artists: Mapped[list[SQLArtist]] = relationship(
        "SQLArtist",
        secondary=song_artists,
        back_populates="songs_artist"
    )
    singers: Mapped[list[SQLArtist]] = relationship(
        "SQLArtist",
        secondary=song_singers,
        back_populates="songs_singer"
    )
    type: Mapped[SongType] = mapped_column(Enum, nullable=False)

    date_released: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    disc: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_copyrighted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    custom_artwork: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    seconds: Mapped[float] = mapped_column(Float, nullable=False)
    audio_references: Mapped[list[AudioReference]] = mapped_column(JSON, nullable=False)
    metadata_source: Mapped[SongMetadataSource] = mapped_column(Enum, nullable=False)

    playlists: Mapped[list["SQLPlaylist"]] = relationship(
        "SQLPlaylist",
        secondary=playlist_songs,
        back_populates="songs"
    )
    
    