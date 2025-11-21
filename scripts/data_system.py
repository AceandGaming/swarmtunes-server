from scripts.manager import *
from scripts.id_manager import IDManager

class DataSystem:
    songs = SongManager()
    albums = AlbumManager()
    users = UserManager()
    playlists = PlaylistManager()
    tokens = TokenManager()