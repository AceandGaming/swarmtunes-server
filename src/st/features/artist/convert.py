from .api import NetworkArtistV2
from .artist import Artist


def to_network_v2(artist: Artist) -> NetworkArtistV2:
    return NetworkArtistV2(name=artist.name, nameOriginal=artist.original_name)


__all__ = ["Artist", "to_network_v2"]
