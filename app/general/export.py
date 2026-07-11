import os
import tempfile
from pathlib import Path
from zlib import adler32

from PIL import Image

from core.paths import ART_CACHE, TEMP


def export_artwork(path: Path, scale: int = 512):
    if not path.exists():
        return None

    name = f"{adler32(str(path).encode())}.webp"
    cache = ART_CACHE / name

    if cache.exists():
        return cache

    with tempfile.NamedTemporaryFile(dir=TEMP, suffix=".tmp", delete=False) as tmp_file:
        temp_path = tmp_file.name

    try:
        image = Image.open(path)
        image = image.resize((scale, scale))
        image.save(temp_path, "webp")

        os.replace(temp_path, cache)

    finally:
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass

    return cache
