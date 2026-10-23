from datetime import datetime

from st.features.artwork import create_path, get_album_artwork
from st.features.song.convert import to_network_v2 as to_network_v2_song

from .album import Album
from .api import NetworkAlbumV1, NetworkAlbumV2


def to_network_v1(album: Album) -> NetworkAlbumV1:
    art = create_path(get_album_artwork(album))

    return NetworkAlbumV1(
        id=str(album.id),
        date=album.date
        and album.date.isoformat()
        or album.last_updated.isoformat(),
        singers=album.songs[0].singer_names,
        cover=art,
        songIds=[str(song.id) for song in album.songs],
    )


def to_network_v2(album: Album) -> NetworkAlbumV2:
    return NetworkAlbumV2(
        id=str(album.id),
        title=album.title,
        artworks=album.artworks,
        date=album.date and album.date.isoformat() or None,
        disc=album.disc,
        songCount=len(album.songs),
        seconds=int(album.seconds),
    )
