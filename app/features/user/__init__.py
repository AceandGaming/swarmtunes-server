from .user import User, UserRoles
from .convert import to_network_v1, to_network_v2
from core.service import Service
from sqlalchemy.orm import Session

def create_user_service(db: Session):
    return Service(db, User)

__all__ = [
    "User",
    "UserRoles",
    "to_network_v1",
    "to_network_v2",
    "create_user_service"
]