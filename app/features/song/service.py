import logging

from sqlalchemy.orm import Session

from core.service import Service
from features.artist import create_or_get
from features.metadata import Metadata
from features.song.song import SongType

from .audio_refrence import AudioReferenceType, SongAudioReference
from .song import Song

log = logging.getLogger()


class SongService(Service[Song]):
    def __init__(self, db: Session):
        super().__init__(db, Song)

    def create_from_metadata(
        self, metadata: Metadata, audio_references: list[SongAudioReference]
    ) -> Song:
        artists = [create_or_get(self._db, a.name, a.name_og) for a in metadata.artists]
        singers = [create_or_get(self._db, a.name, a.name_og) for a in metadata.singers]

        song = Song(
            title=metadata.title,
            title_original=metadata.title_og,
            type=("mashup" in metadata.title.lower() and SongType.MASHUP or SongType.COVER),
            date_released=metadata.date,
            disc=metadata.disc,
            artists=artists,
            singers=singers,
            is_copyrighted=any(a.type == AudioReferenceType.YOUTUBE for a in audio_references),
            seconds=metadata.seconds,
            metadata_source=metadata.source,
        )
        song.audio_references = list(audio_references)

        self.add(song)
        return song

    def update_with_metadata(self, song: Song, metadata: Metadata) -> Song:
        log.debug(f"Updating song {song.title} with metadata {metadata}")
        song.title = metadata.title
        song.title_original = metadata.title_og
        song.date_released = metadata.date
        song.disc = metadata.disc
        song.artists.clear()
        song.artists.extend([create_or_get(self._db, a.name, a.name_og) for a in metadata.artists])
        song.singers.clear()
        song.singers.extend([create_or_get(self._db, a.name, a.name_og) for a in metadata.singers])

        self._db.flush()
        return song
