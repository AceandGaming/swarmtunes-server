from .serializer import BaseSerializer
from scripts.types import Token
from dataclasses import asdict
from datetime import datetime

class TokenSerializer(BaseSerializer):
    @staticmethod
    def Serialize(item: Token):
        data = asdict(item)
        data["expires"] = item.expires.isoformat()
        return data

    @staticmethod
    def Deserialize(data: dict):
        data["expires"] = datetime.fromisoformat(data["expires"])
        return Token(**data)

    @staticmethod
    def SerializeToNetwork(item: Token):
        return {
            "id": item.id,
            "expires": item.expires
        }