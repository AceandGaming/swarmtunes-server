from abstract.id_object import SQLIDObject
from core.database import Base
from sqlalchemy import Column, String, Integer, Boolean, Float, Table, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from typing import Literal, Optional, TypedDict

song_artists = Table(
    "song_artists",
    Base.metadata,
    Column("song_id", String, ForeignKey("songs.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True)
)

song_singers = Table(
    "song_singers",
    Base.metadata,
    Column("song_id", String, ForeignKey("songs.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True)
)

class SQLArtist(Base):
    __tablename__ = "artists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    songs_artist = relationship(
        "Song",
        secondary=song_artists,
        back_populates="artists"
    )

    songs_singer = relationship(
        "Song",
        secondary=song_singers,
        back_populates="singers"
    )

class AudioReference(TypedDict):
    type: Literal["gdrive", "youtube", "audio"]
    id: str

class SQLSong(SQLIDObject):
    __tablename__ = "songs"

    title: Mapped[str] = mapped_column(String, nullable=False)
    title_original: Mapped[Optional[str]] = mapped_column(String)

    artists: Mapped[list[SQLArtist]] = relationship(
        "Artist",
        secondary=song_artists,
        back_populates="songs_artist"
    )
    singers: Mapped[list[SQLArtist]] = relationship(
        "Artist",
        secondary=song_singers,
        back_populates="songs_singer"
    )
    type: Mapped[Literal["original", "collab", "cover"]] = mapped_column(String, nullable=False)

    date_released: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    disc: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_copyrighted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    custom_artwork: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    seconds: Mapped[float] = mapped_column(Float, nullable=False)
    audio_references: Mapped[list[AudioReference]] = mapped_column(JSON, nullable=False)
    metadata_source: Mapped[Literal["json", "id3", "manual"]] = mapped_column(String, nullable=False)
    
    