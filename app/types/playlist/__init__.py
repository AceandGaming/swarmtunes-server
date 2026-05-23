from .playlist import Playlist
from .json import NetworkPlaylistV1, NetworkPlaylistV2
from database.models.playlist import SQLPlaylist
from types.song import to_sql as song_to_sql, from_sql as song_from_sql

def get_singers(playlist: Playlist) -> list[str]:
    pass

def to_network_v1(playlist: Playlist) -> NetworkPlaylistV1:
    return NetworkPlaylistV1(
        id=playlist.id,
        title=playlist.title,
        singers=get_singers(playlist),
        date=playlist.date_created.isoformat(),
        cover=playlist.artwork,
        songIds=[song.id for song in playlist.songs]
    )

def to_network_v2(playlist: Playlist) -> NetworkPlaylistV2:
    return NetworkPlaylistV2(
        id=playlist.id,
        title=playlist.title,
        artwork=playlist.artwork,
        songIds=[song.id for song in playlist.songs],
        dateCreated=playlist.date_created.isoformat()
    )

def to_sql(playlist: Playlist) -> SQLPlaylist:
    return SQLPlaylist(
        # methods from id object
        id = playlist.id,
        date_created = playlist.date_created,
        disabled_at = playlist.disabled_at,
        hidden=playlist.hidden,

        title = playlist.title,
        artwork = playlist.artwork,
        protected = playlist.protected,

        songs = [song_to_sql(song) for song in playlist.songs]
    )

def from_sql(playlist: SQLPlaylist) -> Playlist:
    return Playlist(
        # methods from id object
        id = playlist.id,
        date_created = playlist.date_created,
        disabled_at = playlist.disabled_at,
        hidden=playlist.hidden,

        title=playlist.title,
        songs=[song_from_sql(song) for song in playlist.songs],
        artwork=playlist.artwork,
        protected=playlist.protected
    )

__all__ = [
    "Playlist",
    "to_network_v1",
    "to_network_v2",
    "to_sql",
    "from_sql"
]