from dataclasses import dataclass, field
from datetime import datetime
from scripts.types import Song
from typing import Optional, Callable, TYPE_CHECKING
if TYPE_CHECKING:
    from scripts.types import User 


@dataclass
class Playlist:
    id: str
    name: str
    userId: str
    date: datetime = field(default_factory=lambda: datetime.now())
    songIds: list[str] = field(default_factory=lambda: [])


    @property
    def songs(self) -> list[Song]:
        if not hasattr(self, "songResolver"):
            return []
        songs = []
        for songId in self.songIds:
            song = self.songResolver(songId)
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
    # @property
    # def user(self) -> Optional["User"]:
    #     if self.userResolver is None:
    #         return None
    #     return self.userResolver(self.userId)
    
    def AddResolver(self, songResolver: Optional[Callable[[str], Optional[Song]]] = None, userResolver: Optional[Callable[[str], Optional["User"]]] = None):
        if songResolver is not None:
            self.songResolver = songResolver
        if userResolver is not None:
            self.userResolver = userResolver
    
    def __repr__(self):
        return f"{", ".join(self.singers)} with {len(self.songs)} songs"
    def __eq__(self, other):
        if not isinstance(other, Playlist) or not isinstance(self, Playlist):
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
        self.songIds.append(song.id)
    def RemoveSong(self, song: Song):
        self.songIds.remove(song.id)