from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.database import Base

if TYPE_CHECKING:
    from features.identity.identity import Identity


class LegacyCredentials(Base):
    __tablename__ = "legacy_creds"

    identity_id: Mapped[int] = mapped_column(
        ForeignKey("identities.id", ondelete="CASCADE"), primary_key=True
    )
    identity: Mapped["Identity"] = relationship(
        "Identity", back_populates="legacy_creds"
    )

    password_hash: Mapped[str]
