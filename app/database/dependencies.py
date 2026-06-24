from .database import SessionLocal
from sqlalchemy.orm import Session
from contextlib import contextmanager
from typing import Generator

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()

@contextmanager
def db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()