import uuid as createUUID
from typing import Literal
from .song import SongManager, Song
from scripts.utils import HasValues
from scripts.filters import Filter

class Album:
    @staticmethod
    def CreateFromJson(json):
        if not HasValues(json, "uuid", "date", "type", "songs"):
            print(f"Warn: Invalid album json: {json}")
            return
        songs = []
        for songUUID in json["songs"]:
            song = SongManager.GetSong(songUUID)
            if song is None:
                print(f"Warn: Invalid song data in album json: {json}")
                return
            songs.append(song)
        return Album(json["date"], json["type"], songs, json["uuid"])
    def __init__(self, date: str, type: Literal["neuro", "evil", "duet", "unknown"] = "unknown", songs: list[Song]|None = None, albumUUID: str|None = None):
        self.date = date
        self.songs = songs if songs is not None else []
        self.type = type

        if albumUUID is None:
            albumUUID = str(createUUID.uuid4())
        while albumUUID in AlbumManager.albums:
            albumUUID = str(createUUID.uuid4())
        self.uuid = albumUUID
    def __repr__(self):
        return f"{self.date} ({self.type}) with {len(self.songs)} songs"
    def __eq__(self, other):
        if not isinstance(other, Album) or not isinstance(self, Album):
            return False
        return self.uuid == other.uuid
    def AddSong(self, song: Song):
        self.songs.append(song)
    def RemoveSong(self, song: Song):
        self.songs.remove(song)
    def ToJson(self):
        uuids = [song.uuid for song in self.songs]
        return {
            "uuid": self.uuid,
            "date": self.date,
            "type": self.type,
            "songs": uuids
        }
    def ToNetworkDict(self, lite = False):
        songJSONs = [
            song.ToNetworkDict() if not lite else song.uuid
            for song in self.songs
        ]
        return {
            "uuid": self.uuid,
            "date": self.date,
            "type": self.type,
            "songs": songJSONs
        }
    def DetermineType(self):
        if len(self.songs) == 0:
            self.type = "unknown"
            return self.type
        counts = {"neuro": 0, "evil": 0, "duet": 0, "mashup": 0}
        for song in self.songs:
            counts[song.type] += 1
        mix = (counts["evil"] + (counts["duet"] + counts["mashup"]) * 0.5) / (counts["neuro"] + counts["evil"] + counts["duet"] + counts["mashup"])
        if mix < 0.33:
            self.type = "neuro"
        elif mix > 0.66:
            self.type = "evil"
        else:
            self.type = "duet"
        return self.type
    
class AlbumManager:
    albums: dict[str, Album] = {}
    @staticmethod
    def GetAlbum(uuid: str):
        return AlbumManager.albums.get(uuid)
    @staticmethod
    def AddAlbum(album: Album):
        AlbumManager.albums[album.uuid] = album
    @staticmethod
    def CreateAlbumsFromSongs(songs: list[Song]):
        createdAlbums = []
        dateToAlbum = {}
        for song in songs:
            if song.date in dateToAlbum:
                album = dateToAlbum[song.date]
            else:
                album = Album(song.date)
                AlbumManager.AddAlbum(album)
                createdAlbums.append(album)
                dateToAlbum[song.date] = album
            album.AddSong(song)
        for album in createdAlbums:
            album.DetermineType()
    @staticmethod
    def GenerateAlbums():
        AlbumManager.albums = {}
        AlbumManager.CreateAlbumsFromSongs(list(SongManager.songs.values()))
    @staticmethod
    def GetAlbums(uuidOnly = False, filters: list[Filter] = []):
        matches = []
        for album in AlbumManager.albums.values():
            for filter in filters:
                if not filter.Match(getattr(album, filter.field, None)):
                    break
            else:
                if uuidOnly:
                    matches.append(album.uuid)
                else:
                    matches.append(album)
        return matches
    @staticmethod
    def ConvertToJson(albums: list[Album]|None = None):
        if albums is None:
            albums = list(AlbumManager.albums.values())
        return [album.ToJson() for album in albums]
    @staticmethod
    def ConvertToNetworkDict(albums: list[Album]|None = None, lite = False):
        if albums is None:
            albums = list(AlbumManager.albums.values())
        return [album.ToNetworkDict(lite) for album in albums]