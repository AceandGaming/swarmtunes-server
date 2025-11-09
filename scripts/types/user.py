from dataclasses import dataclass, field
from typing import Optional, Callable, TYPE_CHECKING
from passlib.context import CryptContext
from datetime import datetime
if TYPE_CHECKING:
    from scripts.types import Playlist 

context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@dataclass
class UserData:
    playlistIds: Optional[list[str]] = field(default_factory=lambda: [])
    
@dataclass
class User:
    id: str
    username: str
    password: str #pre-hashed
    date: datetime = field(default_factory=lambda: datetime.now())
    userData: UserData = field(default_factory=lambda: UserData())

    def AddResolver(self, playlistResolver: Callable[[str], Optional["Playlist"]]):
        self.playlistResolver = playlistResolver

    @property
    def validAdmin(self) -> bool:
        if not hasattr(self, "adminHash") or self.adminHash is None:
            return False
        return context.verify(self.id, self.adminHash)

    @property
    def playlists(self) -> list["Playlist"]:
        if not hasattr(self, "playlistResolver"):
            print("Warning: User does not have a playlist resolver")
            return []
        playlists = []
        for playlistId in self.userData.playlistIds or []:
            playlist = self.playlistResolver(playlistId)
            if playlist is not None:
                playlists.append(playlist)
        return playlists
    
    def PromoteUser(self, admin: "User"):
        if not admin.validAdmin:
            raise PermissionError(f"Cannot promote `{self.id}`. User `{admin.id}` is not a valid admin")
        self.adminHash = context.hash(self.id)

    def AddPlaylist(self, playlist: "Playlist"):
        if self.userData.playlistIds is None:
            self.userData.playlistIds = []
        self.userData.playlistIds.append(playlist.id)
    def RemovePlaylist(self, playlist: "Playlist"):
        if self.userData.playlistIds is None:
            return
        if playlist.id not in self.userData.playlistIds:
            return
        self.userData.playlistIds.remove(playlist.id)
    