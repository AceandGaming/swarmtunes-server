from pathlib import Path
import scripts.api.google_drive as google_drive
import scripts.api.rclone as rclone_api
import multiprocessing
import concurrent.futures
from scripts.types.song import Song, SongExternalStorage
from scripts.data_system import DataSystem
from pydub import AudioSegment, silence
import scripts.paths as paths
import pyloudnorm as loudnorm
import numpy as np
import asyncio
from aiohttp import ClientSession
import os
import warnings
from scripts.id_manager import IDManager
import scripts.load_metadata as metadata
from scripts.check_audio import compare_audio_perceptual as CompareAudio
from datetime import datetime
from scripts.cover import CreateArtworkFromSingers

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

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
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
        artists=data.artists,
        singers=data.singers,
        date=data.date or datetime.min,
        storage=SongExternalStorage(googleDriveId=driveFile["id"]),
        coverArt=CreateArtworkFromSingers(data.singers)
    )
    similar = DataSystem.songs.GetSimilar(song)
    if similar is not None:
        print(f"Duplicate song: {song.title} by {song.artists}")
        song.id = similar.id

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
                artists=data.artists,
                singers=data.singers,
                date=data.date or datetime.min,
                storage=SongExternalStorage(googleDriveId=driveFile["id"]),
                coverArt=CreateArtworkFromSingers(data.singers)
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

def _ProcessSong(driveFile: dict, rclone_dir: Path, mp3_dir: Path):
    rel_path = str(driveFile["name"])
    file_path = rclone_dir / rel_path

    if not file_path.exists():
        print(f"File missing after download: {rel_path}")
        return None

    print(f"Processing '{rel_path}' ID: {driveFile['id']}")

    filename = os.path.basename(rel_path)
    nameData = metadata.MetadataFromFilename(filename)

    try:
         audioData = metadata.MetadataFromAudioData(file_path)
    except Exception:
         audioData = metadata.AudioMetadata()

    data = metadata.MergeMetadata(audioData, nameData)

    id = IDManager.NewId(Song) 
    song = Song(
        id=id,
        title=data.titleTranslate or data.title or "unknown",
        artists=data.artists,
        singers=data.singers,
        date=data.date or datetime.min,
        storage=SongExternalStorage(googleDriveId=driveFile["id"]),
        coverArt=CreateArtworkFromSingers(data.singers)
    )
    similar = DataSystem.songs.GetSimilar(song)
    if similar is not None:
        print(f"Duplicate song: {song.title} by {song.artists}")
        song.id = similar.id

    try:
        CorrectMP3(file_path, mp3_dir / song.id)
    except Exception as e:
        print(f"Failed to correct song {song.title}: {e}")
        return None

    return song

async def DownloadMissingSongsRClone() -> None:
    """Downloads missing songs using RClone for bulk download and processing."""
    rclone_dir = paths.PROCESSING_DIR / "rclone_dump"
    rclone_dir.mkdir(parents=True, exist_ok=True)

    print("Fetching file list from RClone...")
    files = await asyncio.to_thread(rclone_api.GetAllFiles)

    driveToUUID = {}
    for song in DataSystem.songs.items:
        if song.storage.googleDriveId is not None:
            driveToUUID[song.storage.googleDriveId] = song

    filesToProcess = []
    for f in files:
        if f["id"] not in driveToUUID:
            filesToProcess.append(f)

    if not filesToProcess:
        print("No new files found.")
        return

    print(f"Found {len(filesToProcess)} new files. Downloading entire drive via RClone...")

    try:
        await asyncio.to_thread(rclone_api.DownloadFiles, str(rclone_dir))
    except Exception as e:
        print(f"RClone download failed: {e}")
        return

    print("Download complete. Processing files...")

    cpu_count = multiprocessing.cpu_count()
    max_workers = min(6, max(1, cpu_count - 2))

    loop = asyncio.get_running_loop()
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=max_workers)
    semaphore = asyncio.Semaphore(max_workers + 2)

    async def _wrapped_process(f):  # Limit to prevent too many concurrent tasks
        async with semaphore:
            return await loop.run_in_executor(executor, _ProcessSong, f, rclone_dir, paths.MP3_DIR)

    try:
        tasks = [asyncio.create_task(_wrapped_process(f)) for f in filesToProcess]

        for task in asyncio.as_completed(tasks):
            try:
                song = await task
                if song:
                    DataSystem.songs.Save(song)
                    print(f"Processed: {song.title}")
            except Exception as e:
                print(f"Error processing song: {e}")

    except asyncio.CancelledError:
        print("\nOperation cancelled. Shutting down workers...")
        executor.shutdown(wait=False, cancel_futures=True)
    finally:
        executor.shutdown(wait=False)

    IDManager.Save()
