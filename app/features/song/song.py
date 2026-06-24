from abstract.id_object import IDObject
from sqlalchemy import JSON, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, mapped_column, Mapped
from datetime import datetime
from typing import Literal, Optional, TYPE_CHECKING
from database.relationships import song_artists, song_singers, playlist_songs, album_songs
from database.types import UTCDateTime
from dataclasses import dataclass
from enum import Enum
if TYPE_CHECKING:
    from features.artist import Artist
    from features.playlist import Playlist
    from features.album import Album

class SongType(Enum):
    ORIGINAL = "original"
    COLLAB = "collab"
    COVER = "cover"
    MASHUP = "mashup"

class SongMetadataSource(Enum):
    JSON = "json"
    ID3 = "id3"
    MANUAL = "manual"

@dataclass
class SongAudio:
    type: Literal["gdrive", "youtube"]
    id: str
    audio_hash: Optional[str] = None

class Song(IDObject):
    __tablename__ = "songs"

    @property
    def duration(self):
        return self.seconds

    @property
    def singers_short(self):
        neuro = "Neuro-sama" in self.singers
        evil = "Evil Neuro" in self.singers
        if neuro and evil:
            return "duet"
        if neuro:
            return "neuro"
        if evil:
            return "evil"
        return None

    @property
    def artist_names(self):
        return [a.name for a in self.artists]

    @property
    def singer_names(self):
        return [a.name for a in self.singers]


    title: Mapped[str] = mapped_column()
    title_original: Mapped[Optional[str]] = mapped_column()

    artists: Mapped[list["Artist"]] = relationship(
        secondary=song_artists,
        back_populates="songs_artist"
    )
    singers: Mapped[list["Artist"]] = relationship(
        secondary=song_singers,
        back_populates="songs_singer"
    )
    type: Mapped[SongType] = mapped_column(SQLAlchemyEnum(SongType))

    date_released: Mapped[datetime] = mapped_column(UTCDateTime())
    disc: Mapped[Optional[int]] = mapped_column()
    is_copyrighted: Mapped[bool] = mapped_column()
    custom_artwork: Mapped[Optional[str]] = mapped_column()

    seconds: Mapped[float] = mapped_column()
    audio_references: Mapped[list[SongAudio]] = mapped_column(JSON)
    metadata_source: Mapped[SongMetadataSource] = mapped_column(SQLAlchemyEnum(SongMetadataSource))

    playlists: Mapped[list["Playlist"]] = relationship(
        secondary=playlist_songs,
        back_populates="songs"
    )
    albums: Mapped[list["Album"]] = relationship(
        secondary=album_songs,
        back_populates="songs"
    )
    

    def __repr__(self):
        artists = " & ".join([a.name for a in self.artists]) if self.artists else "unknown"
        singers = "".join(s[0] for s in self.singer_names if s) or "?"

        return f"'{self.title}' by '{artists}' ({singers}) [{str(self.id)[:5]}]"
    
    def get_audio(self, type: str) -> SongAudio | None:
        return next((a for a in self.audio_references if a.type == type), None)
    