from .api import NetworkUserV1, NetworkUserV2
from .user import User


def to_network_v1(user: User) -> NetworkUserV1:
    return NetworkUserV1(
        username=user.username,
        userData={"playlists": [str(playlist.id) for playlist in user.playlists]},
    )


def to_network_v2(user: User) -> NetworkUserV2:
    return NetworkUserV2(username=user.username, role=user.role.value)
