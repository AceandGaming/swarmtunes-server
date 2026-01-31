from multiprocessing import Process, Pool, Queue, cpu_count
from scripts.correct import CorrectMP3
import scripts.api.rclone_api as rclone
from scripts.api.rclone_api import DriveFile
from pathlib import Path
import scripts.load_metadata as md
import scripts.paths as paths
from scripts.id_manager import IDManager
from scripts.types import *
from scripts.types.song import SongExternalStorage
from datetime import datetime
from scripts.cover import CreateArtworkFromSingers
from scripts.data_system import DataSystem
import os
import logging
import scripts.config as config
import textwrap

logger = logging.getLogger(__name__)

RCLONE_DUMP = paths.PROCESSING_DIR / "rclone_dump"
CORRECT = paths.PROCESSING_DIR / "correct"

def _GetMetadata(file: DriveFile):
    path = RCLONE_DUMP / file.path

    if not path.exists():
        raise FileNotFoundError("Missing mp3 in rclone dump: " + str(path))

    nameData = md.MetadataFromFilename(file.filename)
    id3Data = md.MetadataFromAudioData(path)
    metadata = md.MergeMetadata(id3Data, nameData)

    artwork = CreateArtworkFromSingers(metadata.singers)
    if artwork is None:
        logger.warning(f"Failed to create artwork for song: '{file.filename}'")

    return metadata, artwork

def _AddNewSong(file: DriveFile):
    logger.debug(f"Adding new song: '{file.filename}' DriveID: {file.id}...")

    metadata, artwork = _GetMetadata(file)
    path = Path(file.path)       

    id = IDManager.NewId(Song) 
    song = Song(
        id=id,
        title=metadata.MainTitle,
        artists=metadata.artists,
        singers=metadata.singers,
        date=metadata.date or datetime.min,
        storage=SongExternalStorage(googleDriveId=file.id),
        coverArt=artwork
    )

    tempPath = CORRECT / song.id
    if tempPath.exists():
        raise FileExistsError("MP3 already exists for song with id: " + song.id)

    try:
        CorrectMP3(RCLONE_DUMP / path, tempPath)
    except Exception as e:
        logger.exception("Error correcting mp3:")
        tempPath.unlink(missing_ok=True)
        return

    if (paths.MP3_DIR / song.id).exists():
        raise FileExistsError("MP3 already exists for song with id: " + song.id)

    os.rename(tempPath, paths.MP3_DIR / song.id)
    DataSystem.songs.Save(song)

    logger.debug(f"Added new song: '{song.title}' SongID: {song.id}!")

def _RedownloadSong(song: Song, file: DriveFile, updateMetadata = False):
    logger.debug(f"ReDownloading '{song.title}' DriveID: {song.storage.googleDriveId}")

    driveId = song.storage.googleDriveId
    if driveId is None:
        raise ValueError(f"Song {song.id} has no Google Drive ID")
    
    path = RCLONE_DUMP / file.path

    if not path.exists():
        raise FileNotFoundError("Missing mp3 in rclone dump: " + str(path))

    if updateMetadata:
        logger.debug(f"Updating metadata for '{song.title}'")

        metadata, artwork = _GetMetadata(file)
        
        song.title = metadata.MainTitle
        song.artists = metadata.artists
        song.singers = metadata.singers
        song.date = metadata.date or song.date
        song.coverArt = artwork or song.coverArt

    tempPath = CORRECT / song.id
    
    if tempPath.exists():
        raise FileExistsError("MP3 already exists for song with id: " + song.id)

    try:
        CorrectMP3(path, tempPath)
    except Exception as e:
        logger.exception("Error correcting mp3:")
        tempPath.unlink(missing_ok=True)
        return
    
    out = paths.MP3_DIR / song.id

    out.unlink(missing_ok=True)

    os.rename(tempPath, out)
    DataSystem.songs.Save(song)

    logger.debug(f"ReDownloaded song: '{song.title}' SongID: {song.id}!")
    
def _ReplaceSong(song: Song, file: DriveFile):
    logger.debug(f"ReDownloading '{song.title}' DriveID: {song.storage.googleDriveId}")

    path = RCLONE_DUMP / file.path

    if not path.exists():
        raise FileNotFoundError("Missing mp3 in rclone dump: " + str(path))

    metadata, artwork = _GetMetadata(file)
    
    song = Song(
        id=song.id,
        title=metadata.MainTitle,
        artists=metadata.artists,
        singers=metadata.singers,
        date=metadata.date or datetime.min,
        storage=SongExternalStorage(googleDriveId=file.id),
        coverArt=artwork
    )

    tempPath = CORRECT / song.id
    
    if tempPath.exists():
        raise FileExistsError("MP3 already exists for song with id: " + song.id)

    try:
        CorrectMP3(path, tempPath)
    except Exception as e:
        logger.exception("Error correcting mp3:")
        tempPath.unlink(missing_ok=True)
        return
    
    out = paths.MP3_DIR / song.id

    out.unlink(missing_ok=True)

    os.rename(tempPath, out)
    DataSystem.songs.Save(song)

    logger.debug(f"Replaced song: '{song.title}' SongID: {song.id}!")

def _FindReplacements(songs: list[Song], files: list[DriveFile]):
    replacements: dict[Song, DriveFile] = {}
    tempSongs = {}
    for file in files:
        metadata, _ = _GetMetadata(file)
        tempSongs[file] = (Song(
            id="temp",
            title=metadata.MainTitle,
            artists=metadata.artists,
            singers=metadata.singers,
            date=metadata.date or datetime.min,
        ))

    for song in songs:
        for file, tempSong in tempSongs.items():
            if song.compare(tempSong):
                replacements[song] = file

    return replacements
        

def Run():
    logger.info("Running maintenance...")

    RCLONE_DUMP.mkdir(exist_ok=True)
    CORRECT.mkdir(exist_ok=True)

    songs = {file.name for file in paths.SONGS_DIR.iterdir()}
    mp3s = {file.name for file in paths.MP3_DIR.iterdir()}

    orphinedSongIds: set[str] = songs - mp3s
    orphinedMp3Ids: set[str] = mp3s - songs

    if len(orphinedMp3Ids & orphinedSongIds) > 0:
        logger.error("Detected inconsistency between mp3s and songs")
        return

    logger.debug(f"Found {len(orphinedMp3Ids)} orphaned mp3s")
    logger.debug(f"Found {len(orphinedSongIds)} orphaned songs")

    logger.info("Scanning drive...")
    driveFiles: dict[str, DriveFile] = {}
    for file in rclone.GetAllFiles():
        driveFiles[file.id] = file

    logger.debug(f"Found {len(driveFiles)} files on drive")

    fileLookup: dict[str, DriveFile] = {}
    songLookup: dict[str, Song] = {}
    newFiles: set[DriveFile] = set()

    for file in driveFiles.values():
        for song in DataSystem.songs.items:
            if not song.storage.googleDriveId:
                continue
            if song.storage.googleDriveId == file.id:
                fileLookup[song.id] = file
                songLookup[file.id] = song
                break
        else:
            newFiles.add(file)


    logger.debug(f"Found {len(newFiles)} new files")

    mp3sToDelete = orphinedMp3Ids

    lostSongs: set[Song] = set() #song that have a drive id but it's not on the drive

    orphinedSongs = set()
    for id in orphinedSongIds:
        song = DataSystem.songs.Get(id)
        if song:
            orphinedSongs.add(song)
        

    for song in DataSystem.songs.items:
        if song.storage.googleDriveId and song.storage.googleDriveId not in driveFiles:
            lostSongs.add(song)

    #songs that are missing mp3s but can be redownloaded
    downloadableOrphined = {fileLookup[song.id] for song in (orphinedSongs - lostSongs) if song.id in fileLookup}

    filesToDownload = newFiles | downloadableOrphined
    redownloadTasks = []

    for file in downloadableOrphined: 
        song = songLookup[file.id]
        redownloadTasks.append((song, file,))

    logger.info(textwrap.dedent(f"""
        Report:
        Files to download: {len(filesToDownload)}

        New songs: {len(newFiles)}
        Songs to redownload: {len(redownloadTasks)}
        MP3s to delete: {len(mp3sToDelete)}
        Songs to replace (estimate): {len(lostSongs)}
    """))

    count = len(DataSystem.songs.items)
    if count == 0:
        logger.warning("No songs in database")

    if count > 0:
        if len(filesToDownload) > count * config.MAX_MAINTENACE_DOWNLOAD_PERCENT:
            logger.error(f"Too many files to download. Download count: {len(filesToDownload)}. Max: {count * config.MAX_MAINTENACE_DOWNLOAD_PERCENT}")
            return
        if len(redownloadTasks) > count * config.MAX_MAINTENACE_REDOWNLOAD_PERCENT:
            logger.error(f"Too many files to redownload. Download count: {len(redownloadTasks)}. Max: {count * config.MAX_MAINTENACE_REDOWNLOAD_PERCENT}")
            return

    logger.info(f"Downloading {len(filesToDownload)} files...")
    rclone.DownloadFiles(list(filesToDownload), str(RCLONE_DUMP))
    logger.info(f"Download complete!")

    songsToBeReplaced = _FindReplacements(list(lostSongs), list(newFiles))
    logger.debug(f"Found {len(songsToBeReplaced)} songs to replace")

    if count > 0:
        if len(mp3sToDelete) + len(songsToBeReplaced) > count * config.MAX_MAINTENACE_DELETE_PERCENT:
            logger.error(f"Too many files to delete. Delete count: {len(mp3sToDelete) + len(songsToBeReplaced)}. Max: {count * config.MAX_MAINTENACE_DELETE_PERCENT}")
            return
    
    refrencelessSongs = lostSongs - set(songsToBeReplaced.keys())
    if len(refrencelessSongs) > 0:
        if len(refrencelessSongs) > 100:
            logger.error(f"Too many songs with no drive refrence. Found: {len(refrencelessSongs)}")
            return
        logger.warning(f"Found {len(refrencelessSongs)} songs with no drive refrence")

    addTasks = []
    for file in newFiles - set(songsToBeReplaced.values()):
        addTasks.append((file,))
    logger.debug(f"Found {len(addTasks)} new songs")

    replaceTasks = []
    for song, file in songsToBeReplaced.items():
        replaceTasks.append((song, file,))
    logger.debug(f"Replacing {len(replaceTasks)} songs")

    logger.info(f"Deleting {len(mp3sToDelete)} mp3s...")
    for path in mp3sToDelete:
        (paths.MP3_DIR / path).unlink(missing_ok=True)

    workerCount = cpu_count() - 1
    logger.debug(f"Using {workerCount} workers")

    logger.info("Running tasks...")
    with Pool(workerCount) as pool:
        pool.starmap(_AddNewSong, addTasks)
        pool.starmap(_ReplaceSong, replaceTasks)
        pool.starmap(_RedownloadSong, redownloadTasks)

    logger.info("Maintenance complete!")