from typing import TypeVar, Generic
from sqlalchemy.orm import Session
from abstract.id_object import IDObject
from uuid import UUID

T = TypeVar("T", bound=IDObject)

class Service(Generic[T]):
    def __init__(self, db: Session, model: type[T]):
        self._db = db
        self._model = model

    def query(self):
        return self._db.query(self._model)

    def get_all(self) -> list[T]:
        return self.query().all()

    def create(self, data: dict) -> T:
        item = self._model(**data)
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def get(self, id: UUID) -> T | None:
        return self.query().filter(self._model.id == id).first()
    
    def get_many(self, ids: list[UUID]) -> list[T]:
        return self.query().filter(self._model.id.in_(ids)).all()

    def delete(self, item: T) -> None:
        self._db.delete(item)
        self._db.commit()