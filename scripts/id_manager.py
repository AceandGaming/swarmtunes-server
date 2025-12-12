import uuid
import scripts.paths as paths
from scripts.types import *
import scripts.types as t

class IDManager:
    _ids: dict[str, list[str]] = {}

    @staticmethod
    def NewId(type: type):
        name = type.__name__.lower()
        if name not in IDManager._ids:
            IDManager._ids[name] = []

        def new():
            nonlocal type
            return name + "_" + str(uuid.uuid4())

        id = new()
        while id in IDManager._ids[name]:
            id = new()
        IDManager._ids[name].append(id)
        return id
    @staticmethod
    def GetIds(type: type):
        name = type.__name__.lower()
        return IDManager._ids.get(name)
    @staticmethod
    def SplitId(id: str):
        type, uuid = id.split("_")
        return type, uuid

    @staticmethod
    def Save():
        pass

    @staticmethod
    def Load():
        def GetIdsOfPath(path):
            ids = []
            for file in path.iterdir():
                ids.append(file.name)
            print(f"Found {len(ids)} ids in {path}")
            return ids

        types = [eval(name) for name in t.__all__]

        IDManager._ids["song"] = GetIdsOfPath(paths.SONGS_DIR)
        IDManager._ids["album"] = GetIdsOfPath(paths.ALBUMS_DIR)
        IDManager._ids["playlist"] = GetIdsOfPath(paths.PLAYLISTS_DIR)
        IDManager._ids["user"] = GetIdsOfPath(paths.USERS_DIR)
        IDManager._ids["token"] = GetIdsOfPath(paths.TOKENS_DIR)

        if len(types) != len(IDManager._ids):
            raise Exception("Number of types in id manager does not match number of script types")