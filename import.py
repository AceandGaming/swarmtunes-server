from scripts.id_manager import IDManager
from scripts.correct import CorrectMP3
import scripts.paths as paths
from datetime import datetime
from pathlib import Path
from scripts.search import *
from scripts.data_system import DataSystem
import socket
import os

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
    
if CheckPort(8000) or CheckPort(8001):
    RequireConfirmation("Server is running. This may cause issues! Continue anyway?", default=False)

importPath = Path("import")

mp3 = importPath / "song"
cover = importPath / "cover"

if not mp3.exists():
    mp3s = list(importPath.glob("*.mp3"))
    if len(mp3s) == 0:
        print("No mp3 found")
        exit()
    if len(mp3s) > 1:
        print("Import folder must only contain one mp3 file")
        exit()
    mp3 = mp3s[0]

if not cover.exists():
    covers = list(importPath.glob("*.png"))
    if len(covers) == 0:
        print("No cover found")
        exit()
    if len(covers) > 1:
        print("Import folder must only contain one cover file")
        exit()
    cover = covers[0]

mp3 = mp3.resolve()
cover = cover.resolve()

print("Found mp3 file: ", mp3.name)
print("Found cover file: ", cover.name)

RequireConfirmation()

title = input("Title: ").strip()
artists = input("Artists: ").split(",")
singers = input("Singers: ").split(",")
date = datetime.min

while True:
    dateStr = input("Date (YYYY-MM-DD): ")
    try:
        date = datetime.strptime(dateStr, "%Y-%m-%d")
        break
    except:
        print("Invalid date format")

singers = [s.strip() for s in singers]

id = IDManager.NewId(Song)
print(f"Creating song with:\nID: {id}\nTitle: {title}\nArtist: {artists}\nSingers: {singers}\nDate: {date}")

RequireConfirmation()

song = Song(
    id=id,
    title=title,
    artists=artists,
    date=date,
    singers=singers
)

processingPath = paths.PROCESSING_DIR / id
outputPath = paths.MP3_DIR / id

if outputPath.exists():
    print("Song with same id already in database")
    exit()

if processingPath.exists():
    RequireConfirmation("Song already being processed, overwrite?", default=False)
    processingPath.unlink(True)

print("Moving files...")
os.rename(mp3, processingPath)
os.rename(cover, paths.COVERS_DIR / id)

print("Correcting mp3...")
CorrectMP3(processingPath, outputPath)
processingPath.unlink()

print("Saving song...")
DataSystem.songs.Save(song)
IDManager.Save()

print("Done!")