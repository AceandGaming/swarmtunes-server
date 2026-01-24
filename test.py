from scripts.id_manager import IDManager
from scripts.types import *
from scripts.serializer import *
from scripts.types.song import SongExternalStorage
from scripts.types.user import UserData
from scripts.data_system import DataSystem
from scripts.download import *
from scripts.api.google_drive import *
from scripts.cover import *
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


# songsToDelete = []
# driveFiles = GetAllFiles()
# ids = [file["id"] for file in driveFiles]

# print(ids)

# for song in DataSystem.songs.items:
#     if song.storage.youtubeId:
#         continue
#     if song.storage.googleDriveId not in ids:
#         print(f"Deleting sourceless song: {song.title} - {song.id}")
#         songsToDelete.append(song.id)
        
# print(len(songsToDelete))