from pathlib import Path
import os

def _create(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


BASE = Path(os.path.dirname(os.path.abspath(__file__)))

# Folders
DATA = _create(BASE / "data")

PERSISTENT_DATA = _create(DATA / "persistent")
AUDIO = _create(PERSISTENT_DATA / "audio")
ARTWORK = _create(PERSISTENT_DATA / "artwork")

TEMP = _create(DATA / "temp")
DOWNLOADS = _create(TEMP / "downloads")
PROCESSING = _create(TEMP / "processing")

CACHE = _create(DATA / "cache")
HLS_CACHE = _create(CACHE / "hls")
EXPORT_CACHE = _create(CACHE / "export")
ART_CACHE = _create(CACHE / "artwork")

BACKUPS = _create(BASE / "backups")
SECRETS = _create(BASE / "secrets")
LOGS = _create(BASE / "logs")