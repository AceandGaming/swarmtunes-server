from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Session

from st.core.service import Service
from st.database.relationships import UserPlaylist

from . import events  # IMPORTANT
from .convert import to_network_v1, to_network_v2
from .playlist import Playlist, PlaylistType

if TYPE_CHECKING:
    from st.features.user.user import User


class PlaylistService(Service[Playlist]):
    def __init__(self, db: Session):
        super().__init__(db, Playlist)

    def get_of_user(self, user: "User") -> list[UserPlaylist]:
        return (
            self.query()
            .join(Playlist.users)
            .with_entities(UserPlaylist)
            .filter(UserPlaylist.user_id == user.id)
            .all()
        )

    def get_in_user(self, user: "User", id: UUID) -> UserPlaylist | None:
        return (
            self.query()
            .join(Playlist.users)
            .with_entities(UserPlaylist)
            .filter(UserPlaylist.user_id == user.id)
            .filter(Playlist.id == id)
            .first()
        )

    def get_many_in_user(
        self, user: "User", ids: list[UUID]
    ) -> list[UserPlaylist]:
        return (
            self.query()
            .join(Playlist.users)
            .with_entities(UserPlaylist)
            .filter(UserPlaylist.user_id == user.id)
            .filter(Playlist.id.in_(ids))
            .all()
        )

    def ensure_liked_songs_playlist(self, user: "User"):
        playlist = (
            self.query()
            .filter(
                self._model.owner_id == user.id,
                self._model.type == PlaylistType.LIKED_SONGS,
            )
            .first()
        )

        if not playlist:
            playlist = Playlist(
                title="Liked Songs",
                type=PlaylistType.LIKED_SONGS,
                user=user,
                custom_artwork="liked_songs",
            )
            self.add(playlist)

        return playlist


def create_playlist_service(db: Session):
    return PlaylistService(db)


__all__ = [
    "Playlist",
    "PlaylistType",
    "to_network_v1",
    "to_network_v2",
    "create_playlist_service",
]
