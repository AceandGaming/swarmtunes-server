from pathlib import Path

SONGS_FILE = "data/songs.json"
ALBUMS_FILE = "data/albums.json"
PLAYLISTS_FILE = "data/playlists.json"
USERS_FILE = "data/users.json"
MUSIC_DIR = Path("data/songs")
SONGS_DIR = Path("data/songs")
PENDING_DIR = Path("data/pending_songs")
COVERS_DIR = Path("covers")
TEST_DIR = Path("test")
PROCESSING_DIR = Path("data/processing_songs")

def ClearProcessing():
    for file in PROCESSING_DIR.iterdir():
        file.unlink()
def ClearPending():
    for file in PENDING_DIR.iterdir():
        file.unlink()