from sqlalchemy.exc import IntegrityError

from .artist import Artist
from .convert import to_network_v2


def create_or_get(session, name: str, original_name: str | None = None) -> Artist:
    try:
        with session.begin_nested():
            artist = session.query(Artist).filter_by(name=name).first()
            if artist:
                return artist

            artist = Artist(name=name, original_name=original_name)
            session.add(artist)
            session.flush()
            return artist

    except IntegrityError:
        session.rollback()
        return session.query(Artist).filter_by(name=name).first()


__all__ = ["Artist", "to_network_v2", "create_or_get"]
