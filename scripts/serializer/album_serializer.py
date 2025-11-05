from .serializer import BaseSerializer
from scripts.types import Album
from dataclasses import asdict
from datetime import datetime

class AlbumSerializer(BaseSerializer[Album]):
    @staticmethod
    def Serialize(item: Album):
        data = {
            "id": item.id,
            "date": item.date.isoformat(),
            "songIds": [song.id for song in item.songs]
        }
        return data
    
    @staticmethod
    def Deserialize(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Album(**data)
    
    @staticmethod
    def SerializeToNetwork(item: Album):
        return asdict(item)
    
    @staticmethod
    def DeserializeFromNetwork(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Album(**data)