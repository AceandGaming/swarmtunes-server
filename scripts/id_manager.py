import uuid
import json
import scripts.paths as paths

class IDManager:
    _ids = {}

    @staticmethod
    def NewId(type: str):
        if type not in IDManager._ids:
            IDManager._ids[type] = []

        def new():
            nonlocal type
            return type + "_" + str(uuid.uuid4())

        id = new()
        while id in IDManager._ids[type]:
            id = new()
        IDManager._ids[type].append(id)
        return id
    @staticmethod
    def GetIds(type: str):
        return IDManager._ids.get(type)
    @staticmethod
    def SplitId(id: str):
        type, uuid = id.split("_")
        return type, uuid
    @staticmethod
    def RemoveId(id: str):
        type, uuid = IDManager.SplitId(id)
        IDManager._ids[type].remove(id)

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