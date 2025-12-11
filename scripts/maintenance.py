from scripts.data_system import DataSystem
from scripts.types import *
import scripts.paths as paths
from scripts.id_manager import IDManager


def CheckForOrphanedSongs():
    songFileIds: set[str] = set()
    mp3FileIds: set[str] = set()
    managerIds: set[str] = set(IDManager.GetIds(Song) or [])

    for file in paths.MP3_DIR.iterdir():
        mp3FileIds.add(file.name)
    for file in paths.SONGS_DIR.iterdir():
        songFileIds.add(file.name)

    allIds = songFileIds | mp3FileIds | managerIds

    for id in allIds:
        inManager = id in managerIds
        inSongFile = id in songFileIds
        inMp3File = id in mp3FileIds
        
        if inManager and inSongFile and inMp3File:
            continue

        if inManager and not inSongFile and not inMp3File:
            print(f"Orphaned id: {id}")
            IDManager.RemoveId(id)
        elif not inManager and inSongFile and not inMp3File:
            print(f"Orphaned song: {id}")
            path = paths.SONGS_DIR / id
            path.unlink()
        elif not inManager and not inSongFile and inMp3File:
            print(f"Orphaned mp3: {id}")
            path = paths.MP3_DIR / id
            path.unlink()
        elif not inManager and inSongFile and inMp3File:
            print(f"Missing id: {id}")
            IDManager.AddId(id)
        else:
            print(f"Unknown: {id}")
            print(f"In manager: {inManager}")
            print(f"In song file: {inSongFile}")
            print(f"In mp3 file: {inMp3File}")

    IDManager.Save()

def CheckForOrphaned(type, path, delete=False):
    fileIds: set[str] = set()
    managerIds: set[str] = set(IDManager.GetIds(type) or [])
    for file in path.iterdir():
        fileIds.add(file.name)

    for id in managerIds:
        if id not in fileIds:
            print(f"Orphaned id: {id}")
            IDManager.RemoveId(id)
    for id in fileIds:
        if id not in managerIds:
            print(f"Orphaned file: {id}")
            path = path / id
            if delete:
                path.unlink()

    IDManager.Save()

def ClearProcessing():
    count = 0
    for file in paths.PROCESSING_DIR.iterdir():
        file.unlink()
        count += 1
    print(f"Deleted {count} files from processing")