from caseconverter import camelcase

from st.features.artwork import create_path, get_playlist_artwork
from st.features.song.convert import to_network_v2 as to_network_v2_song

from .api import NetworkPlaylistV1, NetworkPlaylistV2
from .playlist import Playlist, PlaylistType


def get_singers(playlist: Playlist) -> list[str]:
    singers = set()
    for song in playlist.songs:
        singers.update([artist.name for artist in song.song.singers])
    return list(singers)


def to_network_v1(
    playlist: Playlist, include_songs: bool = False
) -> NetworkPlaylistV1:
    art = create_path(get_playlist_artwork(playlist))

    return NetworkPlaylistV1(
        id=str(playlist.id),
        title=playlist.title,
        singers=get_singers(playlist),
        date=playlist.date_created.isoformat(),
        cover=art,
        songIds=[str(song.song.id) for song in playlist.songs],
    )


def to_network_v2(playlist: Playlist) -> NetworkPlaylistV2:
    return NetworkPlaylistV2(
        id=str(playlist.id),
        title=playlist.title,
        seconds=int(playlist.seconds),
        artworks=playlist.artworks,
        type=camelcase(playlist.type.value),  # pyright: ignore[reportArgumentType]
        songCount=len(playlist.songs),
        dateCreated=playlist.date_created.isoformat(),
    )


__all__ = ["Playlist", "to_network_v1", "to_network_v2"]
