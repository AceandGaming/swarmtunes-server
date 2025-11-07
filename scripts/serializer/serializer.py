from typing import Generic, TypeVar
from abc import ABC, abstractmethod

T = TypeVar("T")

class BaseSerializer(ABC, Generic[T]):
    @staticmethod
    @abstractmethod
    def Serialize(item: T):
        raise NotImplementedError
    
    @classmethod
    def SerializeAll(cls, items: list[T]):
        return [cls.Serialize(item) for item in items]

    @staticmethod
    @abstractmethod
    def SerializeToNetwork(item: T):
        raise NotImplementedError
    
    @classmethod
    def SerializeAllToNetwork(cls, items: list[T]):
        return [cls.SerializeToNetwork(item) for item in items]

    @staticmethod
    @abstractmethod
    def Deserialize(data: dict) -> T:
        raise NotImplementedError
