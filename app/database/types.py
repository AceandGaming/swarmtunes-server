from sqlalchemy.types import TypeDecorator, String
from datetime import datetime, timezone

class UTCDateTime(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)

        return value.isoformat()

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return datetime.fromisoformat(value)