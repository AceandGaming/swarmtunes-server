from dataclasses import dataclass, field
from typing import Optional, Callable

@dataclass
class UserData:
    playlistIds: Optional[list[str]] = None
    
@dataclass
class User:
    id: str
    username: str
    password: str #hashed
    userData: UserData = field(default_factory=lambda: UserData())

    def AddResolver(self, resolver: Callable[[str], Optional["Playlist"]]):
        self.playlistResolver = resolver

    @property
    def playlists(self):
        if self.playlistResolver is None or self.userData.playlistIds is None:
            return []
        return [self.playlistResolver(id) for id in self.userData.playlistIds]
    