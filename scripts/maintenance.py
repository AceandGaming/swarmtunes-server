from scripts.data_system import DataSystem
from scripts.types import *
import scripts.paths as paths
import os


def CheckForOrphanedSongs():
    songFileIds: set[str] = set()
    mp3FileIds: set[str] = set()

    for file in paths.MP3_DIR.iterdir():
        mp3FileIds.add(file.name)
    for file in paths.SONGS_DIR.iterdir():
        songFileIds.add(file.name)

    allIds = songFileIds | mp3FileIds

    for id in allIds:
        inSongFile = id in songFileIds
        inMp3File = id in mp3FileIds
        
        if inSongFile and inMp3File:
            continue

        if inSongFile and not inMp3File:
            print(f"Deleting orphaned song: {id}")
            os.remove(paths.SONGS_DIR / id)
            continue

        if not inSongFile and inMp3File:
            print(f"Deleting orphaned mp3: {id}")
            os.remove(paths.MP3_DIR / id)
            continue



def ClearProcessing():
    count = 0
    for file in paths.PROCESSING_DIR.iterdir():
        file.unlink()
        count += 1
    print(f"Deleted {count} files from processing")