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
        data = {
            "id": item.id,
            "title": item.title,
            "artist": item.artist,
            "singers": item.singers,
            "coverType": item.coverType,
            "coverArt": item.coverArt,
            "date": item.date,
            "original": item.isOriginal,
        }
        if item.coverArt is not None:
            data["coverArt"] = item.coverArt
        return data
    
    @staticmethod
    def DeserializeFromNetwork(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Song(**data)