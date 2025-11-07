from .serializer import BaseSerializer
from scripts.types import Playlist
from dataclasses import asdict
from datetime import datetime

class PlaylistSerializer(BaseSerializer[Playlist]):
    @staticmethod
    def Serialize(item: Playlist):
        data = asdict(item)
        data["date"] = item.date.isoformat()
        return data
    
    @staticmethod
    def Deserialize(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Playlist(**data)
    
    @staticmethod
    def SerializeToNetwork(item: Playlist):
        return asdict(item)
    
    @staticmethod
    def DeserializeFromNetwork(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Playlist(**data)