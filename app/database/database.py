from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from core.paths import DATA

DATABASE_URL = "sqlite:///" + str(DATA / "database.db")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def create():
    import features.album
    import features.artist
    import features.identity
    import features.playlist
    import features.session
    import features.share
    import features.song
    import features.user

    Base.metadata.create_all(bind=engine)
