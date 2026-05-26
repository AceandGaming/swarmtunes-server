from dataclasses import dataclass, field
from typing import Optional, Literal
from datetime import datetime
from abstract.id_object import IDObject
from enum import Enum

class SongType(Enum):
    ORIGINAL = "original"
    COLLAB = "collab"
    COVER = "cover"
    MASHUP = "mashup"

class SongMetadataSource(Enum):
    JSON = "json"
    ID3 = "id3"
    MANUAL = "manual"

@dataclass
class SongAudio:
    type: Literal["gdrive", "youtube"]
    id: str
    audio_hash: Optional[str] = None

@dataclass(eq=False, kw_only=True)
class Song(IDObject):
    @property
    def duration(self):
        return self.seconds
    @property
    def singers_short(self):
        neuro = "Neuro-sama" in self.singers
        evil = "Evil Neuro" in self.singers
        if neuro and evil:
            return "duet"
        if neuro:
            return "neuro"
        if evil:
            return "evil"
        return None
    title: str
    title_original: Optional[str] = None

    artists: list[str]
    singers: list[str] # Typically 'Neuro-sama' or 'Evil Neuro'
    type: SongType = SongType.COVER

    date_released: datetime
    disc: Optional[int] = None
    is_copyrighted: bool
    custom_artwork: Optional[str] = None

    seconds: float
    audio_references: list[SongAudio] = field(default_factory=lambda: [])
    metadata_source: SongMetadataSource

    def __repr__(self):
        artists = " & ".join(self.artists) if self.artists else "unknown"
        singers = "".join(s[0] for s in self.singers if s) or "?"

        return f"'{self.title}' by '{artists}' ({singers}) [{self.id[:5]}]"
    
    def get_audio(self, type: str) -> SongAudio | None:
        return next((a for a in self.audio_references if a.type == type), None)