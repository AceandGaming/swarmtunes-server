from .artwork import Artwork
from .song import get_song_artwork
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.album.album import Album
    from features.playlist.playlist import Playlist

def get_collection_artwork(collection: "Album | Playlist") -> list[Artwork]:
    if collection is None:
        return []
    art = set()

    for song in collection.songs:
        art.update(get_song_artwork(song))

    if collection.custom_artwork is not None:
        art.add(Artwork("custom", collection.custom_artwork))

    return list(art)