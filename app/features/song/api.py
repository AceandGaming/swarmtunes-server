from typing import Literal, Optional, TypedDict

from features.artist.api import NetworkArtistV2


class NetworkSongV1(TypedDict):
    id: str
    title: str
    artist: str
    artists: list[str]
    singers: list[str]
    cover: Optional[str]
    coverArt: Optional[str]  # same as above
    date: str
    isOriginal: bool
    youtubeId: Optional[str]
    seconds: int


class NetworkSongV2Lite(TypedDict):
    id: str
    title: str

    artists: list[NetworkArtistV2]
    singers: list[NetworkArtistV2]
    artworks: dict[str, str]

    dateReleased: str


class NetworkSongV2(TypedDict):
    id: str
    title: str
    titleOriginal: Optional[str]

    artists: list[NetworkArtistV2]
    singers: list[NetworkArtistV2]
    type: Literal["original", "collab", "cover", "mashup"]

    dateReleased: str
    seconds: int

    artworks: dict[str, str]

    playable: bool
    audioType: str
    audioId: str
    drmProtected: bool
