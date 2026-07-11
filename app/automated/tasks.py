from core.backup import create_backup, trim_backups
from database.dependencies import db_session

from .albums import update_albums
from .cleanup import sync_cleanup
from .delete import (
    delete_empty_albums,
    delete_old_id_objects,
    delete_old_tokens,
    delete_songless_artists,
)
from .download_missing import download_missing
from .sync import sync


def song_sync_task():
    try:
        with db_session() as db:
            sync(db)
    except:
        raise
    finally:
        sync_cleanup()

    with db_session() as db:
        update_albums(db)


def delete_old_task():
    with db_session() as db:
        delete_old_id_objects(db)
        delete_old_tokens(db)


def delete_orphaned_task():
    with db_session() as db:
        delete_empty_albums(db)
        delete_songless_artists(db)


def download_missing_task():
    with db_session() as db:
        download_missing(db)


def lite_backup_task():
    create_backup(False)


def full_backup_task():
    create_backup(True)


def trim_backups_task():
    trim_backups()
