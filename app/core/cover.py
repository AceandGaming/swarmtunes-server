from PIL import Image
from core.paths import ARTWORK, ART_CACHE, TEMP
from zlib import adler32
from features.song import Song
import os
import tempfile

class Artwork:
    def __init__(self, type: str, name: str):
        self.type = type
        self.name = name

def get_song_artwork(song: Song) -> list[Artwork]:
    if song is None:
        return []
    art = []

    if song.disc is not None:
        art.append(Artwork("disc", str(song.disc)))
    short = song.singers_short
    if short is not None:
        art.append(Artwork("default", short))
        art.append(Artwork("plush", short))
    if song.custom_artwork is not None:
        art.append(Artwork("custom", song.custom_artwork))

    return art

# def get_collection_artwork(collection: SongCollection) -> list[Artwork]:
#     type, name = collection.artwork.split("/")
#     return [Artwork(type, name)]

def get_artwork_path(artwork: Artwork):
    return ARTWORK / f"{artwork.type}/{artwork.name}.png"

def export_artwork(artwork: Artwork, scale: int = 512):
    path = get_artwork_path(artwork)
    if not path.exists():
        return None

    name = f"{adler32(str(path).encode())}.webp"
    cache = ART_CACHE / name

    if cache.exists():
        return cache

    with tempfile.NamedTemporaryFile(dir=TEMP, suffix=".tmp", delete=False) as tmp_file:
        temp_path = tmp_file.name

    try:
        image = Image.open(path)
        image = image.resize((scale, scale))
        image.save(temp_path, "webp")

        os.replace(temp_path, cache)

    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass

    return cache