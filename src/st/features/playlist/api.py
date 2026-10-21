from typing import Literal, Optional, TypedDict


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
    type: str

    songCount: int
    seconds: int
