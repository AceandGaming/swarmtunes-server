from .artwork import Artwork
from .collection import get_collection_artwork
from .song import get_song_artwork


def create_path(arts: list[Artwork]):
    artworks = {artwork.type: f"{artwork.type}/{artwork.name}" for artwork in arts}
    art = (
        artworks.get("custom")
        or artworks.get("default")
        or artworks.get("disc")
        or artworks.get("plush")
    )

    return art


__all__ = ["Artwork", "get_song_artwork", "get_collection_artwork", "create_path"]
