from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from abstract.id_object import IDObject
from core.config import get_config
from database.database import Base
from features.album import Album
from features.artist import Artist
from features.session import Token


def _delete_check(query_count: int, all_count: int):
    max_delete = get_config().automated.max_delete_percent

    if (
        max_delete > 0
        and all_count > 0
        and query_count / all_count > max_delete
    ):
        raise Exception(
            f"Too many objects to delete! About to delete {query_count}/{all_count} objects"
        )


def delete_old_id_objects(db: Session):
    config = get_config().automated

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=config.max_deleted_days
    )

    old = []
    all_count = 0

    for mapper in Base.registry.mappers:
        cls = mapper.class_
        if isinstance(cls, type) and issubclass(cls, IDObject):
            old.extend(db.query(cls).filter(cls.deleted_at < cutoff).all())
            all_count += db.query(cls).count()

    if len(old) == 0:
        return
    _delete_check(len(old), all_count)

    for obj in old:
        db.delete(obj)


def delete_old_tokens(db: Session):
    config = get_config().automated

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=config.max_token_expiry_days
    )
    query = db.query(Token).filter(Token.expires_at < cutoff)

    query.delete()


def delete_empty_albums(db: Session):
    query = db.query(Album).filter(~Album.songs.any())
    all = db.query(Album)

    if query.count() == 0:
        return
    _delete_check(query.count(), all.count())

    for album in query.all():
        album.mark_deleted()


def delete_songless_artists(db: Session):
    query = db.query(Artist).filter(
        ~Artist.songs_artist.any() & ~Artist.songs_singer.any()
    )
    all = db.query(Artist)

    if query.count() == 0:
        return
    _delete_check(query.count(), all.count())

    query.delete()  # Artists can't be soft deleted
