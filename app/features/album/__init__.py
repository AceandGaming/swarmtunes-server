from .album import Album, AlbumType
from .convert import to_network_v1, to_network_v2
from core.service import Service
from sqlalchemy.orm import Session

def create_album_service(db: Session):
    return Service(db, Album)

__all__ = [
    "Album",
    "AlbumType",
    "to_network_v1",
    "to_network_v2"
]