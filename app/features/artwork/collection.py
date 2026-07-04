from typing import TYPE_CHECKING

from .artwork import Artwork
from .song import get_song_artwork

if TYPE_CHECKING:
    from features.album.album import Album
    from features.playlist.playlist import Playlist


def get_collection_artwork(collection: "Album | Playlist") -> list[Artwork]:
    if collection is None:
        return []

    art_count: dict[str, dict[str, int]] = {}

    for song in collection.songs:
        artworks = get_song_artwork(song)
        for artwork in artworks:
            if artwork.type in art_count:
                if artwork.name in art_count[artwork.type]:
                    art_count[artwork.type][artwork.name] += 1
                else:
                    art_count[artwork.type][artwork.name] = 1
            else:
                art_count[artwork.type] = {artwork.name: 1}

    arts = set()
    for type, art_group in art_count.items():
        name = max(art_group, key=lambda art: art_group[art])
        arts.add(Artwork(type, name))

    if collection.custom_artwork is not None:
        arts.add(Artwork("custom", collection.custom_artwork))

    return list(arts)
