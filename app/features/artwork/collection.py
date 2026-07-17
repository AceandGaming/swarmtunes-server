from typing import TYPE_CHECKING

from .artwork import Artwork
from .song import get_song_artwork

if TYPE_CHECKING:
    from features.album.album import Album
    from features.playlist.playlist import Playlist
    from features.song.song import Song


def get_artwork_from_songs(songs: list["Song"]) -> list[Artwork]:
    art_count: dict[str, dict[str, int]] = {}

    for song in songs:
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

    return list(arts)


def get_album_artwork(album: "Album") -> list[Artwork]:
    arts = get_artwork_from_songs(album.songs)
    if album.custom_artwork is not None:
        arts.append(Artwork("custom", album.custom_artwork))
    return arts


def get_playlist_artwork(playlist: "Playlist") -> list[Artwork]:
    arts = get_artwork_from_songs([song.song for song in playlist.songs])
    for art in arts.copy():
        if art.type == "custom":
            arts.remove(art)

    if playlist.custom_artwork is not None:
        arts.append(Artwork("custom", playlist.custom_artwork))

    return arts
