from database.database import Base
from sqlalchemy import Table, Column, String, Integer, ForeignKey

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

playlist_songs = Table(
    "playlist_songs",
    Base.metadata,
    Column("playlist_id", ForeignKey("playlists.id"), primary_key=True),
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
)

album_songs = Table(
    "album_songs",
    Base.metadata,
    Column("album_id", ForeignKey("albums.id"), primary_key=True),
    Column("song_id", ForeignKey("songs.id"), primary_key=True),
)