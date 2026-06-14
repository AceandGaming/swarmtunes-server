from .playlist import Playlist
from .convert import to_network_v1, to_network_v2
from core.service import Service
from sqlalchemy.orm import Session

def create_playlist_service(db: Session):
    return Service(db, Playlist)

__all__ = [
    "Playlist",
    "to_network_v1",
    "to_network_v2",
    "create_playlist_service"
]