from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

@dataclass
class SongExternalStorage:
    googleDriveId: Optional[str] = None
    

@dataclass
class Song:
    id: str
    title: str
    artist: str
    singers: list[str]
    date: datetime
    isOriginal: Optional[bool] = False
    coverArt: Optional[str] = None
    storage: SongExternalStorage = field(default_factory=lambda: SongExternalStorage())

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
        return None
        

    def __repr__(self):
        return f"{self.title} by {self.artist} ({", ".join(self.singers)})"
    def __eq__(self, other):
        if not isinstance(other, Song) or not isinstance(self, Song):
            return False
        return self.id == other.id