from .manager import BaseManager
from scripts.manager import SongManager
from scripts.database import AlbumDatabase
from scripts.types import Album
from scripts.id_manager import IDManager


class AlbumManager(BaseManager[Album]):
    def __init__(self):
        super().__init__(AlbumDatabase())
    
    def Create(self, **kwargs) -> Album:
        id = IDManager.NewId(Album)
        album = Album(id=id, **kwargs)
        self.Save(album)
        return album
    
    def Get(self, id: str):
        album = self._database.Get(id)
        if album is None:
            return None
        
        album.AddResolver(SongManager().Get)
        return album
    
    def CreateFromDate(self, date):
        id = IDManager.NewId(Album)
        songs = []
        for song in SongManager().items:
            print(song.date, date)
            if song.date == date:
                songs.append(song.id)
        album = Album(id=id, date=date, songIds=songs)
        
        album.AddResolver(SongManager().Get)
        self.Save(album)
        return album