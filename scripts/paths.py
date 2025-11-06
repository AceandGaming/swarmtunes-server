from pathlib import Path
import os

DATA_PATH = Path("data")
IDS_FILE = DATA_PATH / "ids.json"
MP3_DIR = DATA_PATH / "mp3"
SONGS_DIR = DATA_PATH / "songs"
ALBUMS_DIR = DATA_PATH / "albums"
USERS_DIR = DATA_PATH / "users"

os.makedirs(MP3_DIR, exist_ok=True)
os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(ALBUMS_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)