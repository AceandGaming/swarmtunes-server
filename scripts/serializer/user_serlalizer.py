from .serializer import BaseSerializer
from scripts.types.user import User, UserData
from dataclasses import asdict
from datetime import datetime

class UserSerializer(BaseSerializer[User]):
    @staticmethod
    def Serialize(item: User):
        data = asdict(item)
        data["date"] = item.date.isoformat()
        return data
    
    @staticmethod
    def Deserialize(data: dict):
        if "date" in data:
            data["date"] = datetime.fromisoformat(data["date"])
        else:
            data["date"] = datetime.now()
        if "userData" in data:
            data["userData"] = UserData(**data["userData"])
        return User(**data)
    
    @staticmethod
    def SerializeToNetwork(item: User):
        return {
            "username": item.username,
            "userData": asdict(item.userData),
        }