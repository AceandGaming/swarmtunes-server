from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from abstract.id_object import IDObject
from core.config import get_config
from features.album import Album
from features.artist import Artist
from features.session import Token


def delete_old_id_objects(db: Session):
    config = get_config()
    if config.automated.max_delete_percent <= 0:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=config.automated.max_deleted_days
    )

    query = db.query(IDObject).filter(IDObject.deleted_at < cutoff)
    all = db.query(IDObject)

    if query.count() == 0:
        return
    if query.count() / all.count() > config.automated.max_delete_percent:
        raise Exception(
            f"Too many objects to delete! About to delete {query.count()}/{all.count()} objects"
        )

    query.delete()


def delete_old_tokens(db: Session):
    config = get_config()
    if config.automated.max_token_expiry_days <= 0:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=config.automated.max_token_expiry_days
    )
    query = db.query(Token).filter(Token.expires_at < cutoff)

    query.delete()


def delete_empty_albums(db: Session):
    config = get_config()

    query = db.query(Album).filter(~Album.songs.any())
    all = db.query(Album)

    if query.count() == 0:
        return
    if query.count() / all.count() > config.automated.max_delete_percent:
        raise Exception(
            f"Too many albums to delete! About to delete {query.count()}/{all.count()} albums"
        )

    query.delete()


def delete_songless_artists(db: Session):
    config = get_config()

    query = db.query(Artist).filter(
        ~Artist.songs_artist.any() & ~Artist.songs_singer.any()
    )
    all = db.query(Artist)

    if query.count() == 0:
        return
    if query.count() / all.count() > config.automated.max_delete_percent:
        raise Exception(
            f"Too many artists to delete! About to delete {query.count()}/{all.count()} artists"
        )

    query.delete()
