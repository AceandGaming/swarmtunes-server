from abstract.id_object import IDObject
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import TYPE_CHECKING
from database.relationships import playlist_songs

if TYPE_CHECKING:
    from ..song.song import Song


class Playlist(IDObject):
    __tablename__ = "playlists"

    title: Mapped[str] = mapped_column()
    artwork: Mapped[str] = mapped_column()

    songs: Mapped[list["Song"]] = relationship(
        "Song",
        secondary=playlist_songs,
        back_populates="playlists"
    )
    protected: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))