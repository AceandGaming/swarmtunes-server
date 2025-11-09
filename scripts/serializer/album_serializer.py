from .serializer import BaseSerializer
from scripts.types import Album
from dataclasses import asdict
from datetime import datetime

class AlbumSerializer(BaseSerializer[Album]):
    @staticmethod
    def Serialize(item: Album):
        data = asdict(item)
        data["date"] = item.date.isoformat()
        return data
    
    @staticmethod
    def Deserialize(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        data["songIds"] = set(data["songIds"])
        return Album(**data)
    
    @staticmethod
    def SerializeToNetwork(item: Album):
        return {
            "id": item.id,
            "date": item.date,
            "type": item.coverType,
            "songIds": list(item.songIds)
        }
    
    @staticmethod
    def DeserializeFromNetwork(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Album(**data)