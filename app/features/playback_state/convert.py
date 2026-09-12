from datetime import datetime, timezone

from .api import NetworkPlaybackStateV2
from .state import PlaybackState


def to_network_v2(state: PlaybackState) -> NetworkPlaybackStateV2:
    return NetworkPlaybackStateV2(
        id=str(state.user_id),
        current_time=state.current_time,
        playing=state.playing,
        shuffle_active=state.shuffle_active,
        queue=state.queue,
        loaded_songs=state.loaded_songs,
    )
