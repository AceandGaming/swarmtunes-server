from .song import Song, SongType
from .convert import to_network_v1, to_network_v2
from core.service import Service
from sqlalchemy.orm import Session

def create_song_service(db: Session):
    return Service(db, Song)

__all__ = [
    "Song",
    "SongType",
    "to_network_v1",
    "to_network_v2",
    "create_song_service"
]