from .serializer import BaseSerializer
from scripts.types.song import Song, SongExternalStorage
from dataclasses import asdict
from datetime import datetime
from scripts.cover import CreateArtworkFromSingers

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

        #convert old json
        if data.get("coverArt") is None:
            data["coverArt"] = CreateArtworkFromSingers(data["singers"])
        if data.get("artist") is not None:
            data["artists"] = data["artist"].split(", ")
            del data["artist"]
        return Song(**data)
    
    @staticmethod
    def SerializeToNetwork(item: Song):
        data = {
            "id": item.id,
            "title": item.title,
            "artist": ", ".join(item.artists), #backward compatibility
            "artists": item.artists,
            "singers": item.singers,
            "cover": item.coverArt,
            "date": item.date,
            "original": item.isOriginal,
            "youtubeId": item.storage.youtubeId
        }
        if item.coverArt is not None:
            data["coverArt"] = item.coverArt
        return data
    
    @staticmethod
    def DeserializeFromNetwork(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        return Song(**data)