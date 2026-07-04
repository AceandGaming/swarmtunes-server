from datetime import datetime, timezone

from sqlalchemy import Enum as SAEnum
from sqlalchemy.types import String, TypeDecorator


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


def StringValueEnum(enum_cls):
    return SAEnum(
        enum_cls,
        native_enum=False,
        values_callable=lambda e: [x.value for x in e],
    )
