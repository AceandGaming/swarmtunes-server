from typing import TYPE_CHECKING
from .manager import BaseManager
from .song_manager import SongManager
from scripts.database import PlaylistDatabase
from scripts.types import Playlist
from scripts.id_manager import IDManager
if TYPE_CHECKING:
    from scripts.types import User 


class PlaylistManager(BaseManager[Playlist]):
    def __init__(self):
        super().__init__(PlaylistDatabase())
    
    def Create(self, **kwargs) -> Playlist:
        id = IDManager.NewId(Playlist)
        playlist = Playlist(id=id, **kwargs)
        playlist.AddResolver(songResolver=SongManager().Get)
        self.Save(playlist)
        return playlist
    
    def Get(self, id: str):
        playlist = self._database.Get(id)
        if playlist is None:
            return None
        
        playlist.AddResolver(songResolver=SongManager().Get)
        return playlist
    
    def GetAll(self):
        playlists = self._database.GetAll()
        for playlist in playlists:
            playlist.AddResolver(songResolver=SongManager().Get)
        return playlists

    def RemoveByUser(self, user: "User"):
        for playlist in user.playlists:
            self.Remove(playlist)