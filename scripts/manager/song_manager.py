from .manager import BaseManager
from scripts.database import SongDatabase
from scripts.types import Song
from scripts.id_manager import IDManager
import scripts.paths as paths

class SongManager(BaseManager[Song]):
    def __init__(self):
        super().__init__(SongDatabase())

    def Create(self, **kwargs) -> Song:
        id = IDManager.NewId(Song)
        song = Song(id=id, **kwargs)
        self.Save(song)
        return song

    def Save(self, item: Song):
        if (paths.COVERS_DIR / item.id).exists():
            item.coverArt = item.id
        elif item.coverArt == item.id:
            item.coverArt = None
        return super().Save(item)
    
    def GetSimilar(self, song: Song) -> Song|None:
        for songItem in self.items:
            if songItem.title == song.title and songItem.artists == song.artists and songItem.date == song.date:
                return songItem