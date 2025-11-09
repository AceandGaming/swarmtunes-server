import scripts.api.google_drive as google_drive
from scripts.types.song import Song, SongExternalStorage
from scripts.data_system import DataSystem
from pydub import AudioSegment, silence
import scripts.paths as paths
import pyloudnorm as loudnorm
import numpy as np
import asyncio
from aiohttp import ClientSession
import os
from scripts.id_manager import IDManager


TARGET_LUFS = -16
MIN_DBFS = -55 #trim audio lower then this

def CorrectMP3(inputFile, output):
    song = AudioSegment.from_file(inputFile, format="mp3")

    silences = silence.detect_silence(song, min_silence_len=300, silence_thresh=MIN_DBFS)
    start = 0
    end = len(song)

    if silences:
        if silences[0][0] == 0:
            start = silences[0][1]
        if silences[-1][1] == len(song):
            end = silences[-1][0]
    song = song[start:end].fade_in(100).fade_out(100)

    samples = np.array(song.get_array_of_samples()) / (1 << 15)
    meter = loudnorm.Meter(song.frame_rate)
    loudness = meter.integrated_loudness(samples)
    samples = loudnorm.normalize.loudness(samples, loudness, TARGET_LUFS)
    samples = np.clip(samples, -1.0, 0.9995) #prevents clipping

    song = song._spawn((samples * (1 << 15)).astype(np.int16).tobytes())

    song.export(output, format="mp3")
def FolderToSingers(folderName):
    match folderName:
        case "neuro":
            return ["Neuro-sama"]
        case "evil":
            return ["Evil Neuro"]
        case "duet":
            return ["Neuro-sama", "Evil Neuro"]
        case "mashup":
            return ["Neuro-sama", "Evil Neuro"]
        case _:
            return ["Unknown"]
def DownloadSong(drive_file):
    print(f"Downloading '{drive_file["name"]}' ID: {drive_file["id"]}")

    google_drive.DownloadFile(drive_file["id"])
    songData = google_drive.GenerateMetaDataFromFile(drive_file["name"])
    id = IDManager.NewId(Song)

    singers = FolderToSingers(drive_file["folder"])

    song = Song(
        id=id,
        storage=SongExternalStorage(drive_file["id"]),
        title=songData["title"],
        artist=songData["artist"],
        date=songData["date"],
        singers=singers
    )
    CorrectMP3(paths.PROCESSING_DIR / drive_file["id"], paths.MP3_DIR / song.id)
    os.remove(paths.PROCESSING_DIR / song.storage.googleDriveId) #type: ignore
    DataSystem.songs.Save(song)

def ReDownloadSong(song):
    print(f"ReDownloading '{song.title}' ID: {song.storage.googleDriveId}")
    if (song.storage.googleDriveId is None):
        return
    if (paths.MP3_DIR / song.id).exists():
        os.remove(paths.MP3_DIR / song.id)
    google_drive.DownloadFile(song.storage.googleDriveId)
    CorrectMP3(paths.PROCESSING_DIR / song.storage.googleDriveId, paths.MP3_DIR / song.id)
    os.remove(paths.PROCESSING_DIR / song.storage.googleDriveId)

async def DownloadSongs(drive_files):
    downloadSemaphore = asyncio.Semaphore(50)
    correctSemaphore = asyncio.Semaphore(6)
    async def CreateSong(drive_file, session: ClientSession):
        async with downloadSemaphore:
            print(f"Downloading '{drive_file["name"]}' ID: {drive_file['id']}")
            await google_drive.DownloadFileAsync(drive_file["id"], session)
            songData = google_drive.GenerateMetaDataFromFile(drive_file["name"])

            id = IDManager.NewId(Song)
            singers = FolderToSingers(drive_file["folder"])
        
            song = Song(
                id=id,
                storage=SongExternalStorage(drive_file["id"]),
                title=songData["title"],
                artist=songData["artist"],
                date=songData["date"],
                singers=singers
            )
            DataSystem.songs.Save(song)
        async with correctSemaphore:
            print(f"Correcting '{song.title}' ID: {song.storage.googleDriveId}")
            if (song.storage.googleDriveId is None):
                return
            await asyncio.to_thread(CorrectMP3, paths.PROCESSING_DIR / song.storage.googleDriveId, paths.MP3_DIR / song.id)
            os.remove(paths.PROCESSING_DIR / song.storage.googleDriveId)

    async with ClientSession() as session:
        tasks = [CreateSong(drive_file, session) for drive_file in drive_files]
        await asyncio.gather(*tasks)

    IDManager.Save()

async def DownloadMissingSongs():
    drive_files = google_drive.GetAllFiles()
    driveToUUID = {}
    for song in DataSystem.songs.items:
        if song.storage.googleDriveId is not None:
            driveToUUID[song.storage.googleDriveId] = song
    filesToDownload = []
    for drive_file in drive_files:
        if drive_file["id"] not in driveToUUID:
            filesToDownload.append(drive_file)
    print(f"Found {len(filesToDownload)} new files to download")
    await DownloadSongs(filesToDownload)