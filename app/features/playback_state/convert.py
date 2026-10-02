from .api import NetworkPlaybackStateV2
from .state import PlaybackState


def to_network_v2(state: PlaybackState) -> NetworkPlaybackStateV2:
    return NetworkPlaybackStateV2(
        currentTime=state.current_time,
        playing=state.playing,
        shuffleActive=state.shuffle_active,
        queue=state.queue,
        loadedSongs=state.loaded_songs,
    )
