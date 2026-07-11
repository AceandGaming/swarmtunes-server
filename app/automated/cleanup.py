import importlib
from shutil import rmtree

import core.paths
from core.paths import CORRECT, DOWNLOADS, TEMP


def sync_cleanup():
    for folder in [CORRECT, DOWNLOADS]:
        for item in folder.iterdir():
            if item.is_dir():
                rmtree(item, ignore_errors=True)
            else:
                item.unlink()


def clear_temp():
    "WARNING: Do NOT use after startup!"
    rmtree(TEMP, ignore_errors=True)
    importlib.reload(core.paths)  # recreate TEMP structure
