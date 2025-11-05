from typing import Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar("T")

class BaseSerializer(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def Serialize(item: T):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def SerializeToNetwork(item: T):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def Deserialize(data: dict) -> T:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def DeserializeFromNetwork(data: dict) -> T:
        raise NotImplementedError