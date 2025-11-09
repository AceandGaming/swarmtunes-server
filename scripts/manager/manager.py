from typing import TypeVar, Generic, Protocol, Type
from scripts.database.database import BaseDatabase
from scripts.id_manager import IDManager

class HasId(Protocol):
    id: str

T = TypeVar("T", bound=HasId)

class BaseManager(Generic[T]):
    @property
    def items(self) -> list[T]:
        return self.GetAll()

    def __init__(self, database: BaseDatabase[T]):
        self._database: BaseDatabase[T] = database

    def Create(self, **kwargs) -> T:
        raise NotImplementedError
    def Save(self, item: T):
        self._database.Save(item)
    def Remove(self, item: T):
        self._database.Remove(item)
        IDManager.RemoveId(item.id)
    def Get(self, id: str):
        return self._database.Get(id)
    def GetAll(self):
        return self._database.GetAll()
         
