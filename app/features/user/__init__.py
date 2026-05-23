from .user import User, Auth
from .json import NetworkUserV1, NetworkUserV2
from database.models.user import SQLUser
from dataclasses import asdict
from datetime import datetime
from features.playlist import from_sql as playlist_from_sql

def to_network_v1(user: User) -> NetworkUserV1:
    return NetworkUserV1(
        username=user.username,
        userData={
            "playlists": [playlist.id for playlist in user.playlists]
        }
    )

def to_network_v2(user: User) -> NetworkUserV2:
    return NetworkUserV2(
        username=user.username,
        playlistIds=[playlist.id for playlist in user.playlists],
        role=user.role.value
    )

def from_sql(user: SQLUser) -> User:
    auth = Auth(
        type=user.auth["type"],
        expires=datetime.fromisoformat(user.auth["expires"]),
        token=user.auth["token"]
    )

    return User(
        # methods from id object
        id=user.id,
        date_created=user.date_created,
        disabled_at=user.disabled_at,
        hidden=user.hidden,

        username=user.username,
        email=user.email,
        auth=auth,
        playlists=[playlist_from_sql(playlist) for playlist in user.playlists],
        role=user.role
    )

def to_sql(user: User) -> SQLUser:
    return SQLUser(
        # methods from id object
        id=user.id,
        date_created=user.date_created,
        disabled_at=user.disabled_at,
        hidden=user.hidden,

        username=user.username,
        email=user.email,
        auth=asdict(user.auth),
        role=user.role
    )

__all__ = [
    "User",
    #"Auth",
    "to_network_v1",
    "to_network_v2",
    "from_sql",
    "to_sql"
]