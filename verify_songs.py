from scripts.id_manager import IDManager
import scripts.paths as paths
from datetime import datetime
from pathlib import Path
from scripts.data_system import DataSystem
from scripts.types import Song
import socket
from scripts.maintenance import ClearAllOrphaned, ClearProcessing
from scripts.load_metadata import *
import scripts.api.google_drive as google_drive
from scripts.serializer import SongSerializer
from prompt_toolkit import prompt
import json

# This isn't 100% accurate and auto mode should be used sparingly

IDManager.Load()

def CheckPort(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def RequireConfirmation(message = "Confirm?", default = True):
    if default:
        response = input(f"{message} (Y/n): ")
        if response.lower() == "n":
            exit()
    else:
        response = input(f"{message} (y/N): ")
        if response.lower() != "y":
            exit()

print("Retrieving google drive files...")
googleDrive = google_drive.GetAllFiles()
googleDriveMetadata = {}
for file in googleDrive:
    googleDriveMetadata[file['id']] = MetadataFromFilename(file['name'])

invalidSongs: list[Song] = []
duplicateSongs: list[Song]  = []
mismatchedSongs: list[Song]  = []

def CheckInvalid(song: Song):
    if song.date > datetime.now():
        return True
    elif song.date < datetime(2000, 1, 1):
        return True
    elif not song.artist or song.artist == "unknown":
        return True
    elif song.title == "unknown":
        return True
    elif song.singers == []:
        return True
    elif not song.isCopywrited and song.storage.googleDriveId is None:
        return True
    return False

def CheckMissmatch(song: Song):
    if song.storage.googleDriveId is None:
        return False
    
    drive = googleDriveMetadata.get(song.storage.googleDriveId)
    if not drive:
        return True
    if drive.title is None or drive.artists is None or drive.singers is None:
        return False
    driveTitle = drive.titleTranslate or drive.title
    if song.title != driveTitle or song.artist != ", ".join(drive.artists) or set(song.singers) != set(drive.singers):
        return True
    return False

def CheckDuplicate(song: Song):
    for otherSong in DataSystem.songs.items:
        if song.id == otherSong.id:
            continue
        if song.title == otherSong.title and song.date == otherSong.date:
            return True
    return False

print("Verifying songs (this may take a while)...")
for i, song in enumerate(DataSystem.songs.items):
    if CheckInvalid(song):
        invalidSongs.append(song)
    elif CheckMissmatch(song):
        mismatchedSongs.append(song)
    elif CheckDuplicate(song):
        duplicateSongs.append(song)
    if i % 50 == 0:
        print(f"Progress: {int(((i + 1) / len(DataSystem.songs.items)) * 100)}%", end="\r")
print("Progress: Done!")
print("Found", len(invalidSongs), "invalid songs")
print("Found", len(duplicateSongs), "duplicate songs")
print("Found", len(mismatchedSongs), "mismatched songs")

RequireConfirmation("Would you like correct the songs?", default=True)
if CheckPort(8000) or CheckPort(8001):
    RequireConfirmation("Server is running. This may cause corruption! Continue anyway?", default=False)

def OverrideWithDrive(song: Song):
    if song.storage.googleDriveId is None:
        return

    if not (paths.PROCESSING_DIR / song.storage.googleDriveId).exists():
        google_drive.DownloadFile(song.storage.googleDriveId)
    audioMetadata = MetadataFromAudioData(paths.PROCESSING_DIR / song.storage.googleDriveId)
    nameMetadata = googleDriveMetadata[song.storage.googleDriveId]
    googleDriveData = MergeMetadata(audioMetadata, nameMetadata)

    if googleDriveData:
        song.title = googleDriveData.titleTranslate or googleDriveData.title or song.title
        song.artist = ", ".join(googleDriveData.artists) or song.artist
        song.singers = googleDriveData.singers or song.singers
        song.date = googleDriveData.date or song.date

    return song

def OverrideWithInput(song: Song):
    title = prompt("Title: ", default=song.title)
    artist = prompt("Artist: ", default=song.artist)
    singers = prompt("Singers: ", default=", ".join(song.singers))
    date = prompt("Date: ", default=song.date.isoformat())

    song.title = title
    song.artist = artist
    song.singers = singers.split(", ")
    song.date = datetime.fromisoformat(date)

    return song

autoOption = None
for i, invalidSong in enumerate(invalidSongs):
    while True:
        print(f"\nInvalid Song ({i+1}/{len(invalidSongs)}):")
        print(json.dumps(SongSerializer.Serialize(invalidSong), indent=2))

        match autoOption or input("What would you like to do? (skip[all] / edit / download / save / exit / auto): ").lower():
            case "skip":
                break
            case "download":
                print("Downloading song...")
                override = OverrideWithDrive(invalidSong)
                if override:
                    invalidSong = override
                    if autoOption:
                        autoOption = "save"
                else:
                    print("Song could not be downloaded")
                    if autoOption:
                        autoOption = "edit"
            case "edit":
                print("Please edit the song manually")
                override = OverrideWithInput(invalidSong)
                if override:
                    invalidSong = override
                    if autoOption:
                        autoOption = "save"
                else:
                    print("Song could not be edited")
                    if autoOption:
                        autoOption = "skip"
            case "save":
                DataSystem.songs.Save(invalidSong)
                if autoOption:
                    autoOption = "download"
                break
            case "exit":
                exit()
            case "auto":
                print("Auto mode enabled")
                autoOption = "download"
            case "skipall":
                autoOption = "skip"
            case _:
                print("Invalid option")
                continue

        if autoOption:
            print("Automatic mode enabled. Next Action: ", autoOption)

        if autoOption == "save" and CheckInvalid(invalidSong):
            print("Song is still invalid")
            autoOption = "edit"

autoOption = None
for i, mismatched in enumerate(mismatchedSongs):
    while True:
        print(f"\nMismatched Song ({i+1}/{len(mismatchedSongs)}):")
        driveData = googleDriveMetadata.get(mismatched.storage.googleDriveId)
        if driveData is None:
            print("Invalid data")
            break
        print("Song data | drive data (filename)")

        print(f"Title:   {mismatched.title:<30} | {driveData.titleTranslate or driveData.title:<30}")
        print(f"Artist:  {mismatched.artist:<30} | {', '.join(driveData.artists):<30}")
        print(f"Singers: {', '.join(mismatched.singers):<30} | {', '.join(driveData.singers):<30}")

        match autoOption or input("What would you like to do? (skip[all] / edit / override / save / exit / auto): ").lower():
            case "skip":
                break
            case "override":
                print("Downloading song...")
                override = OverrideWithDrive(mismatched)
                if override:
                    mismatched = override
                    if autoOption:
                        autoOption = "save"
                else:
                    print("Song could not be downloaded")
                    if autoOption:
                        autoOption = "edit"
            case "edit":
                print("Please edit the song manually")
                override = OverrideWithInput(mismatched)
                if override:
                    mismatched = override
                    if autoOption:
                        autoOption = "save"
                else:
                    print("Song could not be edited")
                    if autoOption:
                        autoOption = "skip"
            case "save":
                DataSystem.songs.Save(mismatched)
                if autoOption:
                    autoOption = "override"
                break
            case "exit":
                exit()
            case "auto":
                print("Auto mode enabled")
                autoOption = "override"
            case "skipall":
                autoOption = "skip"
            case _:
                print("Invalid option")
                continue

        if autoOption:
            print("Automatic mode enabled. Next Action: ", autoOption)

        if autoOption == "save" and CheckInvalid(mismatched):
            print("Song is still invalid")
            autoOption = "edit"

for duplicate in duplicateSongs:
    print(f"Duplicate song: {duplicate.title} by {duplicate.artist}")
    print("ID: ", duplicate.id)
            
    

print("Deleting files in processing...")
ClearProcessing()

print("Regenerating albums...")
DataSystem.albums.ReGenerate()

print("Clearing orphaned...")
ClearAllOrphaned()

print("Done!")