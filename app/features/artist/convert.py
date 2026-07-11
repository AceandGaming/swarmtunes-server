from .artist import Artist
from .api import NetworkArtistV2

def to_network_v2(artist: Artist) -> NetworkArtistV2:
    return {
        "name": artist.name,
        "originalName": artist.original_name
    }

__all__ = [
    "Artist",
    "to_network_v2"
]