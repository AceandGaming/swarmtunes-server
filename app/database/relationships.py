from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, Table
from sqlalchemy import Uuid as SqlAlchemyUuid
from sqlalchemy.orm import relationship

from database.database import Base

from .types import UTCDateTime

song_artists = Table(
    "song_artists",
    Base.metadata,
    Column(
        "song_id",
        SqlAlchemyUuid,
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "artist_id",
        Integer,
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

song_singers = Table(
    "song_singers",
    Base.metadata,
    Column(
        "song_id",
        SqlAlchemyUuid,
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "artist_id",
        Integer,
        ForeignKey("artists.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class PlaylistSong(Base):
    __tablename__ = "playlist_songs"

    playlist_id = Column(
        SqlAlchemyUuid,
        ForeignKey("playlists.id", ondelete="CASCADE"),
        primary_key=True,
    )
    song_id = Column(
        SqlAlchemyUuid,
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    )
    date_added = Column(
        UTCDateTime, nullable=False, default=datetime.now(timezone.utc)
    )

    song = relationship("Song", back_populates="playlists")
    playlist = relationship("Playlist", back_populates="songs")


album_songs = Table(
    "album_songs",
    Base.metadata,
    Column(
        "album_id",
        SqlAlchemyUuid,
        ForeignKey("albums.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "song_id",
        SqlAlchemyUuid,
        ForeignKey("songs.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
