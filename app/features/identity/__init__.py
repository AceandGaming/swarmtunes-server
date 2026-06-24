from .identity import Identity, AuthProvider
from .legacy_creds import LegacyCredentials
from core.service import Service
from sqlalchemy.orm import Session

def create_identity_service(db: Session):
    return Service(db, Identity)

__all__ = [
    "create_identity_service",
    "Identity",
    "AuthProvider",
    "LegacyCredentials"
]