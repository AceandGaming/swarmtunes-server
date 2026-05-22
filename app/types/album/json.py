from typing import TypedDict

class NetworkAlbumV1(TypedDict):
    id: str
    date: str
    coverArt: str
    songIds: list[str]

class NetworkAlbumV2(TypedDict):
    title: str
    artwork: str
    songIds: list[str]
    