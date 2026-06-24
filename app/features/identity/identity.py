from abstract.id_object import IDObject
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import ForeignKey, Enum as SQLAlchemyEnum, UniqueConstraint
from typing import TYPE_CHECKING
from enum import Enum
if TYPE_CHECKING:
    from features.user.user import User
    from features.identity.legacy_creds import LegacyCredentials

class AuthProvider(Enum):
    GOOGLE = "google"
    DISCORD = "discord"
    LEGACY = "legacy"

class Identity(IDObject):
    __tablename__ = "auths"
    
    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(
        "User",
        back_populates="identities"
    )
    provider: Mapped[AuthProvider] = mapped_column(SQLAlchemyEnum(AuthProvider))
    provider_id: Mapped[str] = mapped_column()

    legacy_creds: Mapped["LegacyCredentials"] = relationship(
        "LegacyCredentials",
        back_populates="identity"
    )

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_id",
            name="uq_auth_provider_identity"
        ),
    )