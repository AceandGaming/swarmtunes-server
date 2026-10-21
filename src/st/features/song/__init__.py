from sqlalchemy.orm import Session

from .audio_refrence import AudioReferenceType, SongAudioReference
from .convert import to_network_v1, to_network_v2
from .service import SongService
from .song import Song, SongCopyrightStatus, SongType


def create_song_service(db: Session):
    return SongService(db)


__all__ = [
    "Song",
    "SongType",
    "SongCopyrightStatus",
    "to_network_v1",
    "to_network_v2",
    "create_song_service",
    "SongAudioReference",
    "AudioReferenceType",
]
