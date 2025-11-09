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
    
    def GetAll(self):
        albums = self._database.GetAll()
        for album in albums:
            album.AddResolver(SongManager().Get)
        return albums
    
    def CreateFromDate(self, date):
        id = IDManager.NewId(Album)
        songs = []
        for song in SongManager().items:
            if song.date == date:
                songs.append(song.id)
        album = Album(id=id, date=date, songIds=set(songs))
        
        album.AddResolver(SongManager().Get)
        self.Save(album)
        return album
    
    def ReGenerate(self):
        dateLookup = {}
        for album in self.items:
            dateLookup[album.date] = album
        for song in SongManager().items:
            album = dateLookup.get(song.date)
            if album is None:
                self.CreateFromDate(song.date)
            else:
                album.AddSong(song)
        
        for album in self.items:
            self.Save(album)
            