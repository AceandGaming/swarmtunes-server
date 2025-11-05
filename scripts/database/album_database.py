from .database import BaseDatabase
import scripts.paths as paths
from scripts.serializer import AlbumSerializer
from scripts.types import Album

class AlbumDatabase(BaseDatabase[Album]):
    def __init__(self):
        super().__init__(AlbumSerializer, paths.ALBUMS_DIR)