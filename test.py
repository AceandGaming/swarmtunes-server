from scripts.id_manager import IDManager
from scripts.types import *
from scripts.serializer import *
from scripts.types.song import SongExternalStorage
from scripts.types.user import UserData
from scripts.data_system import DataSystem
from scripts.download import *
from scripts.api.google_drive import *
import scripts.paths as paths
from datetime import datetime
import json
from pathlib import Path
import os
from scripts.search import *
import time
import scripts.maintenance as maintenance
from scripts.delete import DeleteManager
from scripts.load_metadata import *

IDManager.Load()

print("Getting files")
files = GetAllFiles()
driveIds = [driveFiles["id"] for driveFiles in files]

for song in DataSystem.songs.items:
    print(song.title)
    if song.storage.googleDriveId and song.storage.googleDriveId not in driveIds:
        print("Not found")
        DeleteManager.DeleteFile(paths.SONGS_DIR / song.id)