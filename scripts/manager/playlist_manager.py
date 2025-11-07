from .manager import BaseManager
from .song_manager import SongManager
from scripts.database import PlaylistDatabase
from scripts.types import Playlist
from scripts.id_manager import IDManager


class PlaylistManager(BaseManager[Playlist]):
    def __init__(self):
        super().__init__(PlaylistDatabase())
    
    def Create(self, **kwargs) -> Playlist:
        id = IDManager.NewId(Playlist)
        playlist = Playlist(id=id, **kwargs)
        self.Save(playlist)
        return playlist
    
    def Get(self, id: str):
        playlist = self._database.Get(id)
        if playlist is None:
            return None
        
        playlist.AddResolver(songResolver=SongManager().Get)
        return playlist