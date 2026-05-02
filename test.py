from scripts.log import logger
from scripts.id_manager import IDManager
from scripts.types import *
from scripts.api.rclone_api import *
from scripts.cover import *
from scripts.data_system import DataSystem

IDManager.Load()

duplicates = set()
likely_duplicates = set()

print("Checking for duplicates")

songs = DataSystem.songs.GetAll()

for i, songA in enumerate(songs):
    for j in range(i + 1, len(songs)):
        songB = songs[j]
        if songA.fingerprint is not None and songB.fingerprint is not None and songA.fingerprint == songB.fingerprint:
            duplicates.add((songA, songB))
        if songA.title.lower() == songB.title.lower() and (songA.date - songB.date).days <= 1 and set(s.lower() for s in songA.singers) == set(s.lower() for s in songB.singers):
            likely_duplicates.add((songA, songB))

both = duplicates & likely_duplicates

print("Same fingerprint:", len(duplicates))
print("Similar Metadata:", len(likely_duplicates))
print("Both:", len(both))

space = set()
for songA, songB in both:
    if songA.id != songB.id:
        space.add(songA)
        space.add(songB)

print("Songs Part of Duplicates:", len(space))


duplicate_songs = {}

for songA, songB in both:
    if songA in duplicate_songs:
        duplicate_songs[songA].add(songB)
    elif songB in duplicate_songs:
        duplicate_songs[songB].add(songA)
    else:
        duplicate_songs[songA] = {songB}

print("Songs With Duplicates:", len(duplicate_songs))

duplicate_count = 0
for song in duplicate_songs:
    duplicate_count += len(duplicate_songs[song])

print("Total Duplicates:", duplicate_count)

sort = []
for song in duplicate_songs:
    sort.append((song, len(duplicate_songs[song])))

sort.sort(key=lambda item: item[1], reverse=True)

for song, count in sort:
    print(f"({count}) {song} [{song.fingerprint[10:20]}]")

