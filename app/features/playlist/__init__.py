from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.orm import Session

from core.service import Service

from .convert import to_network_v1, to_network_v2
from .playlist import Playlist, PlaylistType

if TYPE_CHECKING:
    from features.user.user import User


class PlaylistService(Service):
    def get_in_user(self, user: "User", id: UUID) -> Playlist | None:
        return self.query().filter(self._model.user_id == user.id, self._model.id == id).first()

    def get_many_in_user(self, user: "User", ids: list[UUID]) -> list[Playlist]:
        return self.query().filter(self._model.user_id == user.id, self._model.id.in_(ids)).all()

    def ensure_liked_songs_playlist(self, user: "User"):
        playlist = (
            self.query()
            .filter(self._model.user_id == user.id, self._model.type == PlaylistType.LIKED_SONGS)
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
    return PlaylistService(db, Playlist)


__all__ = ["Playlist", "PlaylistType", "to_network_v1", "to_network_v2", "create_playlist_service"]
