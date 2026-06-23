from typing import TypedDict, Optional
from song.api import NetworkSongV2

class NetworkAlbumV1(TypedDict):
    id: str
    date: str
    singers: list[str]
    cover: Optional[str]
    songIds: list[str]

class NetworkAlbumV2(TypedDict):
    id: str

    title: str
    artworks: dict[str, str]
    date: Optional[str]
    lastUpdated: Optional[str]

    songs: list[str] | list[NetworkSongV2]
    seconds: int