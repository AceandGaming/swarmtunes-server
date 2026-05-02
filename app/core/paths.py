from pathlib import Path
import os

DELETED_DIR = Path("deleted")
DATA_DIR = Path(os.getenv("DATA_PATH") or "data")
SECRETS_DIR = Path(os.getenv("SECRETS_PATH") or "secrets")
COVERS_DIR = Path("covers")
COVER_CACHE = Path("cache", "covers")
PROCESSING_DIR = Path("processing")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(COVER_CACHE, exist_ok=True)
os.makedirs(PROCESSING_DIR, exist_ok=True)

MP3_DIR = DATA_DIR / "mp3"
SONGS_DIR = DATA_DIR / "songs"
ALBUMS_DIR = DATA_DIR / "albums"
USERS_DIR = DATA_DIR / "users"
PLAYLISTS_DIR = DATA_DIR / "playlists"
TOKENS_DIR = DATA_DIR / "tokens"


os.makedirs(MP3_DIR, exist_ok=True)
os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(ALBUMS_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)
os.makedirs(PLAYLISTS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)
os.makedirs(TOKENS_DIR, exist_ok=True)

SHARE_FILE = DATA_DIR / "shares.json"