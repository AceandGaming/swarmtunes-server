from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy.orm import Session

from abstract.id_object import IDObject

T = TypeVar("T", bound=IDObject)


class Service(Generic[T]):
    def __init__(self, db: Session, model: type[T]):
        self._db = db
        self._model = model

    def query(self, include_disabled=False):
        if include_disabled:
            return self._db.query(self._model)

        return self._db.query(self._model).filter(
            self._model.deleted_at.is_(None)
        )

    def get_all(self) -> list[T]:
        return self.query().all()

    def add(self, item: T) -> T:
        self._db.add(item)
        self._db.flush()
        return item

    def get(self, id: UUID) -> T | None:
        return self.query().filter(self._model.id == id).first()

    def get_many(self, ids: list[UUID]) -> list[T]:
        return self.query().filter(self._model.id.in_(ids)).all()

    def delete(self, item: T) -> None:
        item.disabled_at = datetime.now(timezone.utc)
