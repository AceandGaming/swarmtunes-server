from .serializer import BaseSerializer
from scripts.types.user import User, UserData
from dataclasses import asdict
from datetime import datetime

class UserSerializer(BaseSerializer[User]):
    @staticmethod
    def Serialize(item: User):
        data = asdict(item)
        return data
    
    @staticmethod
    def Deserialize(data: dict):
        data["date"] = datetime.fromisoformat(data["date"])
        if "storage" in data:
            data["storage"] = UserData(**data["storage"])
        return User(**data)
    
    @staticmethod
    def SerializeToNetwork(item: User):
        return {
            "username": item.username,
            "userData": asdict(item.userData),
        }