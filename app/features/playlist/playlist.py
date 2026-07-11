from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abstract.id_object import IDObject
from database.relationships import PlaylistSong
from database.types import StringValueEnum

if TYPE_CHECKING:
    from features.song.song import Song
    from features.user.user import User


class PlaylistType(StrEnum):
    USER = "user"
    LIKED_SONGS = "liked_songs"


class Playlist(IDObject):
    __tablename__ = "playlists"

    @property
    def protected(self):
        return self.type != PlaylistType.USER

    title: Mapped[str]
    custom_artwork: Mapped[Optional[str]]

    songs: Mapped[list[PlaylistSong]] = relationship(
        "PlaylistSong",
        order_by=PlaylistSong.date_added,
        cascade="all, delete-orphan",
    )
    type: Mapped[PlaylistType] = mapped_column(
        StringValueEnum(PlaylistType), default=PlaylistType.USER
    )

    user_id = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    user: Mapped[Optional["User"]] = relationship(
        "User", back_populates="playlists"
    )

    def add_song(self, song: "Song"):
        self.songs.append(PlaylistSong(song=song))

    def remove_song(self, song: "Song"):
        for s in self.songs:
            if s.song == song:
                self.songs.remove(s)
                break
