from scripts.id_manager import IDManager
from scripts.types import *
from scripts.serializer import *
from scripts.types.song import SongExternalStorage
from scripts.types.user import UserData
from scripts.data_system import DataSystem
import scripts.paths as paths
from datetime import datetime
import json
from pathlib import Path
import os

IDManager.Load()

OLD_SONGS_JSON = Path("old_data", "static", "songs.json")
OLD_PLAYLISTS_JSON = Path("old_data", "release", "playlists.json")

with open(OLD_SONGS_JSON, "r") as f:
    old_songs = json.load(f)

with open(OLD_PLAYLISTS_JSON, "r") as f:
    old_playlists = json.load(f)

def GetSongFromOldJson(uuid):
    oldSong = None
    for song in old_songs:
        if song["uuid"] == uuid:
            oldSong = song
            break
    if oldSong is None:
        return

    for id in IDManager.GetIds(Song): #type: ignore
        song = DataSystem.songs.Get(id)
        if song is None:
            continue
        if song.title == oldSong["title"] and song.artist == oldSong["artist"] and song.coverType == oldSong["type"]:
            return song

def ConvertPlaylistJSON(oldJson):
    songs = []
    for song in oldJson["songs"]:
        song = GetSongFromOldJson(song)
        if song is None:
            continue
        songs.append(song.id)

    id = IDManager.NewId(Playlist)
    playlist = Playlist(id=id, name=oldJson["title"], songIds=songs, userId="temp")
    DataSystem.playlists.Save(playlist)
    return playlist


for playlist in old_playlists:
    playlist = ConvertPlaylistJSON(playlist)

IDManager.Save()