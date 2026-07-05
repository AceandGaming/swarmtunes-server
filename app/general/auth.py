import hmac
import logging
import secrets
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from uuid import UUID

from argon2 import PasswordHasher
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.config import get_config
from features.identity import AuthProvider, Identity, LegacyCredentials
from features.session import Token
from features.user import User

log = logging.getLogger()


class AuthManager:
    def __init__(self, db: Session):
        self._db = db
        self._hasher = PasswordHasher()

    def safe_query_identity(self):
        return self._db.query(Identity).filter(Identity.disabled_at.is_(None))

    def safe_query_user(self):
        return self._db.query(User).filter(User.disabled_at.is_(None))

    def safe_query_token(self):
        return self._db.query(Token).filter(Token.disabled_at.is_(None))

    def signup_legacy(self, username: str, password: str):
        """Returns None if the username already exists."""
        hash = self._hasher.hash(password)
        try:
            user = User(username=username)

            identity = Identity(provider=AuthProvider.LEGACY, provider_id=username)
            user.identities.append(identity)
            self._db.add(user)

            self._db.flush()

            legacy = LegacyCredentials(identity_id=identity.id, password_hash=hash)
            self._db.add(legacy)
        except IntegrityError:
            # log.exception("Failed to create user")
            return None

        return identity

    def login_legacy(self, username: str, password: str):
        identity = (
            self.safe_query_identity()
            .filter(Identity.provider == AuthProvider.LEGACY, Identity.provider_id == username)
            .first()
        )
        if not identity:
            return None
        if not identity.legacy_creds:
            log.error(f"Identity type is legacy but no legacy credentials was found. {identity}")
            return None

        try:
            self._hasher.verify(identity.legacy_creds.password_hash, password)
        except Exception:
            return None

        return identity

    def create_token(self, identity: Identity):
        config = get_config()
        secret = secrets.token_urlsafe(32)
        token = Token(
            secret_hash=sha256(secret.encode("utf-8")).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=config.token_expiry_hours),
            identity_id=identity.id,
            user_id=identity.user_id,
        )
        self._db.add(token)

        return secret, token

    def verify_token(self, id: UUID, secret: str):
        token = self.safe_query_token().filter(Token.id == id).first()
        if not token:
            return None
        if token.expired:
            return None
        if not hmac.compare_digest(token.secret_hash, sha256(secret.encode("utf-8")).hexdigest()):
            return None

        return token
