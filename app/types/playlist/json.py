from typing import TypedDict

class NetworkPlaylistV1(TypedDict):
    id: str
    title: str
    singers: list[str]
    date: str
    cover: str
    songIds: list[str]

class NetworkPlaylistV2(TypedDict):
    id: str
    title: str
    artwork: str
    songIds: list[str]
    dateCreated: str