from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from .id_object import IDObject

@dataclass
class SongExternalStorage:
    googleDriveId: Optional[str] = None
    youtubeId: Optional[str] = None
    

@dataclass(eq=False)
class Song(IDObject):
    title: str
    artist: str
    singers: list[str]
    date: datetime
    isOriginal: bool = False
    coverArt: Optional[str] = None
    storage: SongExternalStorage = field(default_factory=lambda: SongExternalStorage())
    isCopywrited: bool = False

    def __post_init__(self):
        self.isCopywrited = self.isCopywrited or self.isOriginal

    @property
    def coverType(self):
        if self.coverArt is not None:
            return "custom"
        if len(self.singers) == 0:
            return None
        if len(self.singers) > 1:
            return "duet"
        singer = self.singers[0]
        if singer == "Neuro-sama":
            return "neuro"
        if singer == "Evil Neuro":
            return "evil"
        if singer == "Hiyori":
            return "v1"
        return None
        

    def __repr__(self):
        return f"{self.title} by {self.artist} ({", ".join(self.singers)})"