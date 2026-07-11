from .artwork import Artwork
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.song.song import Song

def get_song_artwork(song: "Song") -> list[Artwork]:
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