from pathlib import Path


def _create(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


BASE = Path(__file__).resolve().parents[2]  # project root
if not (BASE / "app").is_dir():
    raise Exception(f"Base path doesn't point to project root! Path {BASE} is missing 'app' folder")

# Folders
DATA = _create(BASE / "data")
CONFIG = _create(BASE / "config")

PERSISTENT_DATA = _create(DATA / "persistent")
AUDIO = _create(PERSISTENT_DATA / "audio")
ARTWORK = _create(PERSISTENT_DATA / "artwork")

TEMP = _create(DATA / "temp")
DOWNLOADS = _create(TEMP / "downloads")
CORRECT = _create(TEMP / "correct")

CACHE = _create(DATA / "cache")
HLS_CACHE = _create(CACHE / "hls")
ART_CACHE = _create(CACHE / "artwork")

BACKUPS = _create(BASE / "backups")
SECRETS = _create(BASE / "secrets")
LOGS = _create(BASE / "logs")
