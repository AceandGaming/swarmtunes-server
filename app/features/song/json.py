from typing import TypedDict, Optional, Literal


class NetworkSongV1(TypedDict):
    id: str
    title: str
    artist: str
    singers: list[str]
    cover: Optional[str]
    date: str
    isOriginal: bool
    youtubeId: Optional[str]

class NetworkSongV2(TypedDict):
    id: str
    title: str
    titleOriginal: Optional[str]

    artists: list[str]
    singers: list[str]
    type: Literal["original", "collab", "cover", "mashup"]

    dateReleased: str
    seconds: int
    artworks: dict[str, str]

    audioType: Literal["audio", "youtube"]
    audioId: str
    drmProtected: bool