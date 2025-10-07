from pathlib import Path
import os

#static
SONGS_FILE = Path("data/static/songs.json")
MUSIC_DIR = Path("data/static/songs")
SONGS_DIR = Path("data/static/songs")

COVERS_DIR = Path("covers")


DATA_PATH = Path("data") / os.getenv("DATA_PATH", "release")
print("Using path", DATA_PATH)

PLAYLISTS_FILE = DATA_PATH / "playlists.json"
USERS_FILE = DATA_PATH / "users.json"
PENDING_DIR = DATA_PATH / "pending_songs"
PROCESSING_DIR = DATA_PATH / "processing_songs"

def ClearProcessing():
    for file in PROCESSING_DIR.iterdir():
        file.unlink()
def ClearPending():
    for file in PENDING_DIR.iterdir():
        file.unlink()