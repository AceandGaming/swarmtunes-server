from .serializer import BaseSerializer
from scripts.types import Album
from dataclasses import asdict
from datetime import datetime
from scripts.cover import CreateArtworkFromSingers

class AlbumSerializer(BaseSerializer[Album]):
    @staticmethod
    def Serialize(item: Album):
        data = asdict(item)
        data["date"] = item.date.isoformat()
        data["songIds"] = list(item.songIds)

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
            "singers": item.singers,
            "cover": item.coverArt,
            "songIds": list(item.songIds)
        }
    
    @staticmethod
    def DeserializeFromNetwork(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Album(**data)