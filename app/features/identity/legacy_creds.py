from database.database import Base
from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import ForeignKey
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.identity.identity import Identity

class LegacyCredentials(Base):
    __tablename__ = "legacy_creds"

    identity_id = mapped_column(
        ForeignKey("identities.id", ondelete="CASCADE"),
        unique=True
    )
    identity: Mapped["Identity"] = relationship(
        "Identity",
        back_populates="legacy_creds"
    )

    password_hash: Mapped[str] = mapped_column()