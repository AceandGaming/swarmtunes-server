from sqlalchemy import Column, ForeignKey, Integer, String, Table
from sqlalchemy import Uuid as SqlAlchemyUuid

from database.database import Base

song_artists = Table(
    "song_artists",
    Base.metadata,
    Column("song_id", SqlAlchemyUuid, ForeignKey("songs.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)

song_singers = Table(
    "song_singers",
    Base.metadata,
    Column("song_id", SqlAlchemyUuid, ForeignKey("songs.id"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artists.id"), primary_key=True),
)

playlist_songs = Table(
    "playlist_songs",
    Base.metadata,
    Column("playlist_id", SqlAlchemyUuid, ForeignKey("playlists.id"), primary_key=True),
    Column("song_id", SqlAlchemyUuid, ForeignKey("songs.id"), primary_key=True),
)

album_songs = Table(
    "album_songs",
    Base.metadata,
    Column("album_id", SqlAlchemyUuid, ForeignKey("albums.id"), primary_key=True),
    Column("song_id", SqlAlchemyUuid, ForeignKey("songs.id"), primary_key=True),
)
