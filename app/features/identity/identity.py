from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from abstract.id_object import IDObject

if TYPE_CHECKING:
    from features.identity.legacy_creds import LegacyCredentials
    from features.user.user import User


class AuthProvider(Enum):
    GOOGLE = "google"
    DISCORD = "discord"
    LEGACY = "legacy"


class Identity(IDObject):
    __tablename__ = "identities"

    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User", back_populates="identities")
    provider: Mapped[AuthProvider] = mapped_column(SQLAlchemyEnum(AuthProvider))
    provider_id: Mapped[str]

    legacy_creds: Mapped["LegacyCredentials"] = relationship(
        "LegacyCredentials", back_populates="identity"
    )

    __table_args__ = (
        UniqueConstraint("provider", "provider_id", name="uq_auth_provider_identity"),
    )
