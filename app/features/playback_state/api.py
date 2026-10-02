from typing import TypedDict


class NetworkPlaybackStateV2(TypedDict):
    currentTime: float
    playing: bool
    shuffleActive: bool

    queue: list[str]
    loadedSongs: list[str]
