from abstract.id_object import IDObject
from sqlalchemy.orm import relationship, mapped_column, Mapped
from sqlalchemy import ForeignKey
from datetime import datetime, timezone
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from features.user.user import User

class Token(IDObject):
    __tablename__ = "tokens"
    @property
    def maxAge(self):
        return (self.expires_at - datetime.now(timezone.utc)).total_seconds()
    @property
    def expired(self):
        return self.maxAge < 0

    user_id = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    identity_id = mapped_column(ForeignKey("identities.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(
        "User",
        back_populates="tokens"
    )

    expires_at: Mapped[datetime] = mapped_column(timezone=True)
    secret_hash: Mapped[str] # Hashed