from .database import SessionLocal
from contextlib import contextmanager

def get_db():
    db = SessionLocal()

    try:
        yield db
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