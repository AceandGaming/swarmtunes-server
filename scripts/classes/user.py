from __future__ import annotations
import scripts.paths as paths
import uuid as createUUID
import json
from passlib.context import CryptContext
from scripts.filters import Filter
from scripts.utils import *
from .song import SongManager, Song
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User:
    @classmethod
    def CreateFromJson(cls, userJson: dict):
        if not HasValues(userJson, "uuid", "username", "password", "playlists"):
            print(f"Warn: Invalid user json: {userJson}")
            return
        playlists = []
        for playlistUUID in userJson["playlists"]:
            playlist = PlaylistManager.GetPlaylist(playlistUUID)
            if playlist is None:
                print(f"Warn: Invalid playlist data in user json: {playlistUUID}")
                return
            playlist.userid = userJson["uuid"]
            playlists.append(playlist)
        user = cls.__new__(cls)
        user.username = userJson["username"]
        user.password = userJson["password"] #already hashed
        user.playlists = playlists
        user.uuid = userJson["uuid"]
        return user
    @property
    def isAdmin(self) -> bool:
        return False

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = pwd_context.hash(password) 
        self.playlists = []

        uuid = str(createUUID.uuid4())
        while uuid in UserManager.users.keys():
            uuid = str(createUUID.uuid4())
        self.uuid = uuid
    def __repr__(self):
        return self.username
    def __eq__(self, other):
        if not isinstance(other, User) or not isinstance(self, User):
            return False
        return self.uuid == other.uuid
    def AddPlaylist(self, playlist: Playlist):
        self.playlists.append(playlist)
    def RemovePlaylist(self, playlist: Playlist):
        self.playlists.remove(playlist)
    def VerifyPassword(self, password: str):
        return pwd_context.verify(password, self.password)
    def ToJson(self):
        playlistUUIDs = [playlist.uuid for playlist in self.playlists]
        return {
            "uuid": self.uuid,
            "username": self.username,
            "password": self.password,
            "playlists": playlistUUIDs
        }
    def ToNetworkDict(self, lite = False):
        playlistJSONs = [
            playlist.ToNetworkDict() if not lite else playlist.uuid
            for playlist in self.playlists
        ]
        return {
            "uuid": self.uuid,
            "username": self.username,
            "playlists": playlistJSONs
        }

class UserManager:
    users = {}
    @staticmethod
    def GetUser(uuid: str):
        return UserManager.users.get(uuid)
    @staticmethod
    def GetUserWithUsername(username: str):
        for user in UserManager.users.values():
            if user.username == username:
                return user
    @staticmethod
    def AddUser(user: User):
        UserManager.users[user.uuid] = user
        UserManager.Save()
    @staticmethod
    def RemoveUser(user: User):
        for playlist in user.playlists:
            PlaylistManager.RemovePlaylist(playlist)
        del UserManager.users[user.uuid]
        UserManager.Save()
    @staticmethod
    def GetUsers(uuidOnly = False, filters: list[Filter] = []):
        matches = []
        for user in UserManager.users.values():
            for filter in filters:
                if not filter.Match(getattr(user, filter.field, None)):
                    break
            else:
                if uuidOnly:
                    matches.append(user.uuid)
                else:
                    matches.append(user)
        return matches
    @staticmethod
    def ConvertToJson(users: list[User]|None = None):
        if users is None:
            users = list(UserManager.users.values())
        return [user.ToJson() for user in users]
    @staticmethod
    def ConvertToNetworkDict(users: list[User]|None = None, lite = False):
        if users is None:
            users = list(UserManager.users.values())
        return [user.ToNetworkDict(lite) for user in users]
    @staticmethod
    def Load():
        with open(paths.USERS_FILE, "r") as file:
            users = json.load(file)
            for userJson in users:
                user = User.CreateFromJson(userJson)
                if user is None:
                    raise Exception(f"Loaded invalid user json: {userJson}")
                UserManager.users[user.uuid] = user
    @staticmethod
    def Save():
        with open(paths.USERS_FILE, "w") as file:
            json.dump(UserManager.ConvertToJson(), file, indent=2)

class Playlist:
    @property
    def user(self) -> User:
        user = UserManager.GetUser(self.userid)
        if user is None:
            raise Exception(f"Playlist has invalid user uuid: {self.userid}")
        return user
    @staticmethod
    def CreateFromJson(json):
        if not HasValues(json, "uuid", "title", "songs"):
            print(f"Warn: Invalid playlist json: {json}")
            return
        songs = []
        for songUUID in json["songs"]:
            song = SongManager.GetSong(songUUID)
            if song is None:
                print(f"Warn: Invalid song data in playlist json: {json}")
                return
            songs.append(song)
        return Playlist(json["title"], "", songs, json["uuid"])
    def __init__(self, title: str, userid: str, songs: list[Song]|None = None, uuid: str|None = None):
        self.title = title
        self.songs = songs if songs is not None else []
        self.userid = userid

        if uuid is None:
            uuid = str(createUUID.uuid4())
        while uuid in PlaylistManager.playlists:
            uuid = str(createUUID.uuid4())
        self.uuid = uuid
    def __repr__(self):
        return f"{self.title} with {len(self.songs)} songs"
    def __eq__(self, other):
        if not isinstance(other, Playlist) or not isinstance(self, Playlist):
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
            "title": self.title,
            "songs": uuids
        }
    def ToNetworkDict(self, lite = False):
        songJSONs = [
            song.ToNetworkDict() if not lite else song.uuid
            for song in self.songs
        ]
        return {
            "uuid": self.uuid,
            "title": self.title,
            "user": self.userid,
            "songs": songJSONs
        }
    
class PlaylistManager:
    playlists: dict[str, Playlist] = {}
    @staticmethod
    def GetPlaylist(uuid: str):
        return PlaylistManager.playlists.get(uuid)
    @staticmethod
    def AddPlaylist(playlist: Playlist):
        PlaylistManager.playlists[playlist.uuid] = playlist
        playlist.user.AddPlaylist(playlist)
        PlaylistManager.Save()
    @staticmethod
    def RemovePlaylist(playlist: Playlist):
        del PlaylistManager.playlists[playlist.uuid]
        playlist.user.RemovePlaylist(playlist)
        PlaylistManager.Save()
    @staticmethod
    def GetPlaylists(filters: list[Filter] = [], playlists: list[Playlist]|None = None):
        matches: list[Playlist] = []
        if playlists is None:
            playlists = list(PlaylistManager.playlists.values())
        for playlist in playlists:
            for filter in filters:
                if not filter.Match(getattr(playlist, filter.field, None)):
                    break
            else:
                matches.append(playlist)
        return matches
    @staticmethod
    def ConvertToJson(playlists: list[Playlist]|None = None):
        if playlists is None:
            playlists = list(PlaylistManager.playlists.values())
        return [playlist.ToJson() for playlist in playlists]
    @staticmethod
    def ConvertToNetworkDict(playlists: list[Playlist]|None = None, lite = False):
        if playlists is None:
            playlists = list(PlaylistManager.playlists.values())
        return [playlist.ToNetworkDict(lite) for playlist in playlists]
    @staticmethod
    def Save():
        with open(paths.PLAYLISTS_FILE, "w") as file:
            json.dump(PlaylistManager.ConvertToJson(), file, indent=2)
    @staticmethod
    def Load():
        with open(paths.PLAYLISTS_FILE, "r") as file:
            playlists = json.load(file)
            for playlistJson in playlists:
                playlist = Playlist.CreateFromJson(playlistJson)
                if playlist is None:
                    raise Exception(f"Loaded invalid playlist json: {playlistJson}")
                PlaylistManager.playlists[playlist.uuid] = playlist