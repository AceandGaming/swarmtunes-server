from dataclasses import dataclass, field
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from types.song import Song


@dataclass
class Album:
    id: int
    title: str
    artwork: str
    songIds: list[str] = field(default_factory=lambda: [])
    
    def add_song(self, *songs: Song):
        for song in songs:
            self.songIds.append(song.id)

    def remove_song(self, *songs: Song):
        for song in songs:
            if song.id not in self.songIds:
                continue
            self.songIds.remove(song.id)

    def __repr__(self):
        return f"'{self.title}' with {len(self.songIds)} songs"

    def __hash__(self) -> int:
        return self.id
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.id == value.id