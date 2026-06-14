from .playlist import Playlist
from .api import NetworkPlaylistV1, NetworkPlaylistV2
from features.playlist.playlist import Playlist

def get_singers(playlist: Playlist) -> list[str]:
    singers = set()
    for song in playlist.songs:
        singers.update([artist.name for artist in song.singers])
    return list(singers)

def to_network_v1(playlist: Playlist) -> NetworkPlaylistV1:
    return NetworkPlaylistV1(
        id=str(playlist.id),
        title=playlist.title,
        singers=get_singers(playlist),
        date=playlist.date_created.isoformat(),
        cover=playlist.artwork,
        songIds=[str(song.id) for song in playlist.songs]
    )

def to_network_v2(playlist: Playlist) -> NetworkPlaylistV2:
    return NetworkPlaylistV2(
        id=str(playlist.id),
        title=playlist.title,
        artwork=playlist.artwork,
        songIds=[str(song.id) for song in playlist.songs],
        dateCreated=playlist.date_created.isoformat()
    )

__all__ = [
    "Playlist",
    "to_network_v1",
    "to_network_v2"
]