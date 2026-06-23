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
    import features.song.song
    import features.artist.artist
    import features.album.album
    import features.playlist.playlist
    import features.user.user
    Base.metadata.create_all(bind=engine)