from .database import BaseDatabase
import scripts.paths as paths
from scripts.serializer import SongSerializer
from scripts.types import Song

class SongDatabase(BaseDatabase[Song]):
    def __init__(self):
        super().__init__(Song, SongSerializer, paths.SONGS_DIR)