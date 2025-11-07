from .database import BaseDatabase
import scripts.paths as paths
from scripts.serializer import PlaylistSerializer
from scripts.types import Playlist

class PlaylistDatabase(BaseDatabase[Playlist]):
    def __init__(self):
        super().__init__(Playlist, PlaylistSerializer, paths.PLAYLISTS_DIR)