import scripts.paths as paths
import uuid as createUUID
from typing import Literal
import json
import os
from scripts.utils import HasValues
from scripts.filters import Filter
from datetime import datetime

class Song:
    @staticmethod
    def CreateFromJson(json):
        if not HasValues(json, "uuid", "title", "type", "artist", "date", "google_drive_id", "original"):
            print(f"Warn: Invalid song json: {json}")
            return
        return Song(json["title"], json["type"], json["artist"], json["date"], json["google_drive_id"], json["original"], json["uuid"])
    @property
    def cover_artist(self):
        return {"neuro": "Neuro-sama", "evil": "Evil Neuro", "duet": "Neuro-sama and Evil Neuro"}[self.type]
    @property
    def cover_art(self):
        if (paths.COVERS_DIR / f"{self.uuid}.png").exists():
            return paths.COVERS_DIR / f"{self.uuid}.png"
        else:
            return paths.COVERS_DIR / f"{self.type}.png"
    @property
    def datetime(self):
        if self.date == "unknown":
            return datetime.min
        else:
            return datetime.strptime(self.date, "%d/%m/%y")

    def __init__(self, title: str, type: Literal["neuro", "evil", "duet"], artist = "unknown", date = "unknown", google_drive_id = "none", is_original = False, songUUID = None):
        self.title = title
        self.type = type
        self.artist = artist
        self.date = date
        self.google_drive_id = google_drive_id
        self.original = is_original

        if songUUID is None:
            songUUID = str(createUUID.uuid4())
        while songUUID in SongManager.songs:
            songUUID = str(createUUID.uuid4())
        self.uuid = songUUID
    def __repr__(self):
        return f"{self.title} by {self.artist} ({self.type})"
    def __eq__(self, other):
        if not isinstance(other, Song) or not isinstance(self, Song):
            return False
        return self.uuid == other.uuid
    def ToJson(self):
        return {
            "uuid": self.uuid,
            "title": self.title,
            "type": self.type,
            "artist": self.artist,
            "date": self.date,
            "google_drive_id": self.google_drive_id,
            "original": self.original
        }
    def ToNetworkDict(self):
        return {
            "uuid": self.uuid,
            "title": self.title,
            "type": self.type,
            "artist": self.artist,
            "date": self.date,
            "original": self.original
        }

class SongManager:
    songs: dict[str, Song] = {}
    @staticmethod
    def GetSong(uuid: str):
        return SongManager.songs.get(uuid)
    @staticmethod
    def AddSong(song: Song):
        if song.uuid in SongManager.songs:
            raise Exception("Song already exists")
        SongManager.songs[song.uuid] = song
    @staticmethod
    def GetSongs(filters: list[Filter] = []):
        matches: list[Song] = []
        for song in SongManager.songs.values():
            for filter in filters:
                if not filter.Match(getattr(song, filter.field, None)):
                    break
            else:
                matches.append(song)
        matches.sort(key=lambda song: song.datetime, reverse=True)
        return matches
    @staticmethod
    def ConvertToJson(songs: list[Song]|None = None):
        if songs is None:
            songs = list(SongManager.songs.values())
        return [song.ToJson() for song in songs]
    @staticmethod
    def ConvertToNetworkDict(songs: list[Song]|None = None):
        if songs is None:
            songs = list(SongManager.songs.values())
        return [song.ToNetworkDict() for song in songs]

    @staticmethod
    def Save():
        with open(paths.SONGS_FILE, "w") as file:
            json.dump(SongManager.ConvertToJson(), file, indent=2)
    @staticmethod
    def Load():
        with open(paths.SONGS_FILE, "r") as file:
            songs = json.load(file)
            for songJson in songs:
                song = Song.CreateFromJson(songJson)
                if song is None:
                    raise Exception(f"Loaded invalid song json: {songJson}")
                SongManager.AddSong(song)
    @staticmethod
    def DeleteSongsWithoutReference():
        if len(SongManager.songs) == 0:
            raise Exception("No songs loaded! aborting cleanup.")
        files = os.listdir(paths.MUSIC_DIR)
        for file in files:
            if SongManager.GetSong(file) is None:
                print(f"Removing '{file}'. No refrence in songs")
                os.remove(paths.MUSIC_DIR / file)