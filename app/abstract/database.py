from typing import Generic, TypeVar, Protocol, Type
from scripts.serializer import BaseSerializer
from pathlib import Path
from scripts.id_manager import IDManager
import json
from scripts.delete import DeleteManager

class HasId(Protocol):
    id: str

T = TypeVar("T", bound=HasId)

class BaseDatabase(Generic[T]):
    def __init__(self, type: Type[T], serializer: Type[BaseSerializer[T]], path: Path):
        self._serializer = serializer
        self._path = path
        self._objectType = type

    def Get(self, id: str):
        path = self._path / id
        if not path.exists():
            print("Warning: No item found with id", id)
            return None
        with open(path, "r") as f:
            data = json.load(f)
            return self._serializer.Deserialize(data)
    
    def GetAll(self) -> list[T]:
        ids = IDManager.GetIds(self._objectType)
        if ids is None:
            print("Warning: No ids found in id manager for type", self._objectType.__name__.lower())
            return []
        items = []
        for id in ids:
            item = self.Get(id)
            if item is not None:
                items.append(item)
        return items
    
    def Remove(self, item: T):
        path = self._path / item.id
        if path.exists():
            DeleteManager.DeleteFile(path)

    def Save(self, item: T):
        path = self._path / item.id
        with open(path, "w") as f:
            string = json.dumps(self._serializer.Serialize(item), indent=2)
            if string is None or string == "":
                raise Exception("Failed to serialize item")
            f.write(string)