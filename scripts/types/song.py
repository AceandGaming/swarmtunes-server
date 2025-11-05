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
    storage: SongExternalStorage = field(default_factory=lambda: SongExternalStorage())

    def __repr__(self):
        return f"{self.title} by {self.artist} ({", ".join(self.singers)})"
    def __eq__(self, other):
        if not isinstance(other, Song) or not isinstance(self, Song):
            return False
        return self.id == other.id