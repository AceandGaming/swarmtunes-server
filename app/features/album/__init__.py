from .album import Album
from .json import NetworkAlbumV1, NetworkAlbumV2
from datetime import datetime

def get_date(album: Album) -> datetime:
    #TODO Return actual date


def to_network_v1(album: Album) -> NetworkAlbumV1:
    return {
        "id": "album_" + str(album.id),
        "date": get_date(album).isoformat(),
        "coverArt": album.artwork,
        "songIds": album.song_ids
    }

def to_network_v2(album: Album) -> NetworkAlbumV2:
    return {
        "title": album.title,
        "artwork": album.artwork,
        "songIds": album.song_ids
    }

__all__ = ["Album", "to_network_v1", "to_network_v2"]