import uuid
import json
import scripts.paths as paths

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
    def RemoveId(id: str):
        name, uuid = IDManager.SplitId(id)
        IDManager._ids[name].remove(id)

    @staticmethod
    def Save():
        with open(paths.IDS_FILE, "w") as f:
            f.write(json.dumps(IDManager._ids, indent=2))
    @staticmethod
    def Load():
        if not paths.IDS_FILE.exists():
            return
        with open(paths.IDS_FILE, "r") as f:
            data = json.load(f)
            IDManager._ids = data