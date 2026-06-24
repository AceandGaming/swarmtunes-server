from abstract.id_object import IDObject
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING, Optional
from database.relationships import playlist_songs
if TYPE_CHECKING:
    from features.song.song import Song
    from features.user.user import User

class Playlist(IDObject):
    __tablename__ = "playlists"

    title: Mapped[str] = mapped_column()
    custom_artwork: Mapped[Optional[str]] = mapped_column()

    songs: Mapped[list["Song"]] = relationship(
        "Song",
        secondary=playlist_songs,
        back_populates="playlists"
    )
    protected: Mapped[bool] = mapped_column(default=False)

    user_id = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="playlists"
    )

    def add_song(self, song: "Song"):
        self.songs.append(song)

    def remove_song(self, song: "Song"):
        self.songs.remove(song)

