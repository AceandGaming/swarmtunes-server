import hashlib
import hmac
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone

from core.config import get_config

IP_SECRET = secrets.token_bytes(32)


def hash_ip(ip: str):
    return hmac.new(IP_SECRET, ip.encode("utf-8"), hashlib.sha256).hexdigest()


class SignupLimit:
    signups: dict[str, int]

    def __init__(self) -> None:
        self.signups = {}
        self.date = datetime.now(timezone.utc).date()

    def on_signup(self, ip: str):
        hash = hash_ip(ip)

        if hash in self.signups:
            self.signups[hash] += 1
        else:
            self.signups[hash] = 1

    def can_signup(self, ip: str):
        config = get_config()

        today = datetime.now(timezone.utc).date()
        if today != self.date:
            self.date = today
            self.signups = {}

        hash = hash_ip(ip)
        signup_count = self.signups.get(hash, 0)
        if signup_count >= config.daily_max_signups_per_ip:
            return False

        return True
