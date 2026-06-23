from typing import TypedDict, Optional, Literal
from features.artist.api import NetworkArtistV2

class NetworkSongV1(TypedDict):
    id: str
    title: str
    artist: str
    artists: list[str]
    singers: list[str]
    cover: Optional[str]
    coverArt: Optional[str] # same as above
    date: str
    isOriginal: bool
    youtubeId: Optional[str]

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

    audioType: Literal["audio", "youtube"]
    audioId: str
    drmProtected: bool