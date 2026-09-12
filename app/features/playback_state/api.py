from typing import Literal, Optional, TypedDict


class NetworkPlaybackStateV2(TypedDict):
    id: str

    current_time: float
    playing: bool
    shuffle_active: bool

    queue: list[str]
    loaded_songs: list[str]
