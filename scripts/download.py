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
import scripts.load_metadata as metadata
from scripts.check_audio import compare_audio_perceptual as CompareAudio
from datetime import datetime

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

def DownloadSong(driveFile):
    print(f"Downloading '{driveFile["name"]}' ID: {driveFile["id"]}")

    google_drive.DownloadFile(driveFile["id"])
    nameData = metadata.MetadataFromFilename(driveFile["name"])
    audioData = metadata.MetadataFromAudioData(paths.PROCESSING_DIR / driveFile["id"])
    data = metadata.MergeMetadata(audioData, nameData)

    id = IDManager.NewId(Song) 
    song = Song(
        id=id,
        title=data.titleTranslate or data.title or "unknown",
        artist=", ".join(data.artists),
        singers=data.singers,
        date=data.date or datetime.min,
        storage=SongExternalStorage(googleDriveId=driveFile["id"])
    )

    CorrectMP3(paths.PROCESSING_DIR / driveFile["id"], paths.MP3_DIR / song.id)
    os.remove(paths.PROCESSING_DIR / driveFile["id"])
    DataSystem.songs.Save(song)

def ReDownloadSong(song: Song):
    driveId = song.storage.googleDriveId
    print(f"ReDownloading '{song.title}' ID: {driveId}")
    if (driveId is None):
        return
    if (paths.MP3_DIR / song.id).exists():
        os.remove(paths.MP3_DIR / song.id)
    google_drive.DownloadFile(driveId)
    metadata.DeleteID3Tags(paths.PROCESSING_DIR / driveId)
    CorrectMP3(paths.PROCESSING_DIR / driveId, paths.MP3_DIR / song.id)
    os.remove(paths.PROCESSING_DIR / driveId)

async def DownloadSongs(drive_files):
    downloadSemaphore = asyncio.Semaphore(35)
    correctSemaphore = asyncio.Semaphore(10)
    async def CreateSong(driveFile, session: ClientSession):
        async with downloadSemaphore:
            print(f"Downloading '{driveFile["name"]}' ID: {driveFile['id']}")
            try:
                await google_drive.DownloadFileAsync(driveFile["id"], session)
            except Exception as e:
                print("Error downloading file:", e)
                return
    
            nameData = metadata.MetadataFromFilename(driveFile["name"])
            audioData = metadata.MetadataFromAudioData(paths.PROCESSING_DIR / driveFile["id"])
            data = metadata.MergeMetadata(audioData, nameData)

            id = IDManager.NewId(Song) 
            song = Song(
                id=id,
                title=data.titleTranslate or data.title or "unknown",
                artist=", ".join(data.artists),
                singers=data.singers,
                date=data.date or datetime.min,
                storage=SongExternalStorage(googleDriveId=driveFile["id"])
            )

            DataSystem.songs.Save(song)
        async with correctSemaphore:
            print(f"Correcting '{song.title}' ID: {song.storage.googleDriveId}")
            if (song.storage.googleDriveId is None):
                return
            try:
                metadata.DeleteID3Tags(paths.PROCESSING_DIR / song.storage.googleDriveId)
                await asyncio.to_thread(CorrectMP3, paths.PROCESSING_DIR / song.storage.googleDriveId, paths.MP3_DIR / song.id)
                os.remove(paths.PROCESSING_DIR / song.storage.googleDriveId)
            except Exception as e:
                print("Failed to correct song:", e)

    async with ClientSession() as session:
        tasks = [CreateSong(driveFile, session) for driveFile in drive_files]
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