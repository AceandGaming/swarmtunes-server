from .album import Album
from .api import NetworkAlbumV1, NetworkAlbumV2
from features.song.convert import to_network_v2 as to_network_v2_song
from datetime import datetime
from features.artwork.collection import get_collection_artwork

def to_network_v1(album: Album) -> NetworkAlbumV1:
    artworks = {artwork.type: f"{artwork.type}/{artwork.name}" for artwork in get_collection_artwork(album)}
    art = artworks["custom"] or artworks["default"] or artworks["plush"] or None

    return NetworkAlbumV1(
        id=str(album.id),
        date=album.date and album.date.isoformat() or datetime.now().isoformat(),
        singers=album.songs[0].singer_names,
        cover=art,
        songIds=[str(song.id) for song in album.songs]
    )

def to_network_v2(album: Album, include_songs: bool = False) -> NetworkAlbumV2:
    if include_songs:
        songs = [to_network_v2_song(song) for song in album.songs]
    else:
        songs = [str(song.id) for song in album.songs]

    seconds = 0
    for song in album.songs:
        seconds += song.seconds

    return NetworkAlbumV2(
        id=str(album.id),
        title=album.title,
        artworks={artwork.type: artwork.name for artwork in get_collection_artwork(album)},
        date=album.date and album.date.isoformat() or None,
        lastUpdated=datetime.now().isoformat(),
        songs=songs,
        seconds=int(seconds)
    )