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
    artists: list[str]
    singers: list[str]
    date: datetime
    duration: Optional[float] = None
    coverArt: Optional[str] = None
    subtitle: Optional[str] = None
    isOriginal: bool = False
    storage: SongExternalStorage = field(default_factory=lambda: SongExternalStorage())
    isCopywrited: bool = False
    fingerprint: Optional[str] = None

    @property
    def prettyArtists(self):
        return ", ".join(self.artists)
    
    @property
    def prettySingers(self):
        return ", ".join(self.singers)

    def __post_init__(self):
        self.isCopywrited = self.isCopywrited or self.isOriginal

    def __repr__(self):
        return f"{self.title} by {" and ".join(self.artists)} ({", ".join(self.singers)})"
    
    def compare(self, other: "Song"):
        """Compare metadata with other song. Returns true if they are similar"""
        if self == other:
            return True
        if self.title == other.title and self.artists == other.artists and self.date == other.date and self.singers == other.singers:
            return True
        return False