from abc import ABC
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from types.song import Song

@dataclass(kw_only=True)
class SongCollection(ABC):
    title: str
    songs: list[Song] = field(default_factory=lambda: [])
    artwork: str

    def __repr__(self):
        return f"'{self.title}' with {len(self.songs)} songs"

    def add_song(self, *songs: Song):
        for song in songs:
            self.songs.append(song)

    def remove_song(self, *songs: Song):
        for song in songs:
            self.songs.remove(song)