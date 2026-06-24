from typing import TypedDict, Optional, Literal

class UserData(TypedDict):
    playlists: list[str]

class NetworkUserV1(TypedDict):
    username: str
    userData: UserData

class NetworkUserV2(TypedDict):
    username: str
    role: Literal["user", "admin"]