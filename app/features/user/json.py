from typing import TypedDict, Optional, Literal

class NetworkUserV1(TypedDict):
    username: str
    userData: dict

class NetworkUserV2(TypedDict):
    username: str
    playlistIds: list[str]
    role: Literal["user", "admin"]