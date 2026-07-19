from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from abstract.id_object import IDObject
from database.relationships import (
    PlaylistSong,
    album_songs,
    song_artists,
    song_singers,
)
from database.types import StringValueEnum, UTCDateTime
from features.metadata.metadata import MetadataSource

if TYPE_CHECKING:
    from features.album import Album
    from features.artist import Artist
    from features.playlist import Playlist

    from .audio_refrence import SongAudioReference


class SongType(StrEnum):
    ORIGINAL = "original"
    COLLAB = "collab"
    COVER = "cover"
    MASHUP = "mashup"


class SongCopyrightStatus(StrEnum):
    ACTIVE = "active"
    COPYRIGHT_CLAIMED = "copyright_claimed"


class Song(IDObject):
    __tablename__ = "songs"

    @property
    def duration(self):
        return self.seconds

    @property
    def singers_short(self):
        neuro = any(["Neuro-sama" == singer.name for singer in self.singers])
        evil = any(["Evil Neuro" == singer.name for singer in self.singers])
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

    title: Mapped[str]
    title_original: Mapped[Optional[str]]

    artists: Mapped[list["Artist"]] = relationship(
        secondary=song_artists, back_populates="songs_artist"
    )
    singers: Mapped[list["Artist"]] = relationship(
        secondary=song_singers, back_populates="songs_singer"
    )
    type: Mapped[SongType] = mapped_column(
        StringValueEnum(SongType),
        index=True,
    )

    date_released: Mapped[datetime] = mapped_column(UTCDateTime())
    disc: Mapped[Optional[int]]
    custom_artwork: Mapped[Optional[str]]

    is_copyrighted: Mapped[bool]
    copyright_status: Mapped[SongCopyrightStatus] = mapped_column(
        StringValueEnum(SongCopyrightStatus), default=SongCopyrightStatus.ACTIVE
    )

    seconds: Mapped[float]
    audio_references: Mapped[list["SongAudioReference"]] = relationship(
        back_populates="song",
        cascade="all, delete-orphan",
    )
    metadata_source: Mapped[MetadataSource] = mapped_column(
        StringValueEnum(MetadataSource)
    )

    playlists: Mapped[list["Playlist"]] = relationship(
        PlaylistSong, back_populates="song"
    )
    albums: Mapped[list["Album"]] = relationship(
        secondary=album_songs, back_populates="songs"
    )

    def __repr__(self):
        artists = (
            " & ".join([a.name for a in self.artists])
            if self.artists
            else "unknown"
        )
        singers = "".join(s[0] for s in self.singer_names if s) or "?"

        return f"'{self.title}' by '{artists}' ({singers}) [{str(self.id)[:5]}]"
