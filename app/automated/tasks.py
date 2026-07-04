from database.dependencies import db_session

from .albums import update_albums
from .cleanup import sync_cleanup
from .sync import sync


def sync_task():
    try:
        sync()
    except:
        raise
    finally:
        sync_cleanup()
    update_albums_task()


def update_albums_task():
    with db_session() as db:
        update_albums(db)
