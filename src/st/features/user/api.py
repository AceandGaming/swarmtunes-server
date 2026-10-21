from typing import Literal, TypedDict
from uuid import UUID


class UserData(TypedDict):
    playlists: list[str]


class NetworkUserV1(TypedDict):
    username: str
    userData: UserData


class NetworkUserV2(TypedDict):
    id: UUID
    username: str
    role: Literal["user", "admin"]
