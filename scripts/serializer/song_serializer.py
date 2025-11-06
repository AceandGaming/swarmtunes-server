from .serializer import BaseSerializer
from scripts.types.song import Song, SongExternalStorage
from dataclasses import asdict
from datetime import datetime

class SongSerializer(BaseSerializer[Song]):
    @staticmethod
    def Serialize(item: Song):
        data = asdict(item)
        data["date"] = item.date.isoformat()
        return data
    
    @staticmethod
    def Deserialize(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        if "storage" in data:
            data["storage"] = SongExternalStorage(**data["storage"])
        return Song(**data)
    
    @staticmethod
    def SerializeToNetwork(item: Song):
        return {
            "id": item.id,
            "title": item.title,
            "artist": item.artist,
            "singers": item.singers,
            "date": item.date,
            "isOriginal": item.isOriginal,
        }
    
    @staticmethod
    def DeserializeFromNetwork(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Song(**data)