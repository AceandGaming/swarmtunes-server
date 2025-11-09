from dataclasses import dataclass, field
from datetime import datetime
from scripts.types.song import Song
from typing import Optional, Callable

@dataclass
class Album:
    id: str
    date: datetime
    songIds: set[str] = field(default_factory=lambda: set())

    @property
    def songs(self) -> list[Song]:
        if not hasattr(self, "resolver"):
            print("Warning: Album does not have a resolver")
            return []
        songs = []
        for songId in self.songIds:
            song = self.resolver(songId)
            if song is not None:
                songs.append(song)
        return songs

    @property
    def singers(self):
        return self._GetSingers()
    
    @property
    def coverType(self):
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
    
    @property
    def PrettyName(self):
        return " and ".join(self.singers) + "Karaoke"

    
    def AddResolver(self, resolver: Callable[[str], Optional[Song]]):
        self.resolver = resolver
    
    def __repr__(self):
        return f"{", ".join(self.singers)} with {len(self.songs)} songs"
    def __eq__(self, other):
        if not isinstance(other, Album) or not isinstance(self, Album):
            return False
        return self.id == other.id


    def _GetSingers(self):
        singers = set()
        singerCounts = {}
        for song in self.songs:
            singers.update(song.singers)
            for singer in song.singers:
                if singer in singerCounts:
                    singerCounts[singer] += 1
                else:
                    singerCounts[singer] = 1
        minPercentage = 1 / (len(singers) + 1)
        totalCount = sum(singerCounts.values())
        newSingers = set()
        for singer in singers:
            percentage = singerCounts[singer] / totalCount
            if percentage > minPercentage:
                newSingers.add(singer)
        return list(newSingers)
    
    def AddSong(self, song: Song):
        self.songIds.add(song.id)
    def RemoveSong(self, song: Song):
        self.songIds.remove(song.id)