from typing import Optional, TypedDict

from features.song.api import NetworkSongV2


class NetworkPlaylistV1(TypedDict):
    id: str
    title: str
    singers: list[str]
    date: str
    cover: Optional[str]
    songIds: list[str]


class NetworkPlaylistV2(TypedDict):
    id: str
    title: str

    artworks: dict[str, str]
    dateCreated: str

    songs: list[str] | list[NetworkSongV2]
    seconds: int
