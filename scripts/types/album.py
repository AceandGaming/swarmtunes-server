from dataclasses import dataclass, field
from datetime import datetime
from scripts.types.song import Song
from typing import Optional, Callable

@dataclass
class Album:
    id: str
    date: datetime
    resolver: Optional[Callable[[str], Optional[Song]]] = None
    songIds: list[str] = field(default_factory=lambda: [])

    @property
    def singers(self):
        return self._GetSingers()

    @property
    def songs(self) -> list[Song]:
        if self.resolver is None:
            return []
        songs = []
        for songId in self.songIds:
            song = self.resolver(songId)
            if song is not None:
                songs.append(song)
        return songs
    
    def __repr__(self):
        return f"{", ".join(self.singers)} with {len(self.songs)} songs"
    def __eq__(self, other):
        if not isinstance(other, Album) or not isinstance(self, Album):
            return False
        return self.id == other.id


    def _GetSingers(self):
        singers = set()
        for song in self.songs:
            singers.update(song.singers)
        return list(singers)
    
    def AddSong(self, song: Song):
        self.songIds.append(song.id)
    def RemoveSong(self, song: Song):
        self.songIds.remove(song.id)