from datetime import datetime, timezone

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from automated.tasks import (
    delete_old_task,
    delete_orphaned_task,
    download_missing_task,
    full_backup_task,
    lite_backup_task,
    song_sync_task,
    trim_backups_task,
)
from core.config import get_config
from core.paths import DATA


def add_automated_tasks(scheduler: AsyncIOScheduler):
    config = get_config().automated

    if config.sync_frequency_hours > 0:
        scheduler.add_job(
            song_sync_task,
            "interval",
            hours=config.sync_frequency_hours,
            id="song_sync",
            next_run_time=datetime.now(tz=timezone.utc),
        )
    if config.delete_old_frequency_hours > 0:
        scheduler.add_job(
            delete_old_task,
            "interval",
            hours=config.delete_old_frequency_hours,
            id="delete_old",
            next_run_time=datetime.now(tz=timezone.utc),
        )
    if config.delete_orphaned_frequency_hours > 0:
        scheduler.add_job(
            delete_orphaned_task,
            "interval",
            hours=config.delete_orphaned_frequency_hours,
            id="delete_orphaned",
            next_run_time=datetime.now(tz=timezone.utc),
        )
    if config.download_missing_audio_frequency_hours > 0:
        scheduler.add_job(
            download_missing_task,
            "interval",
            hours=config.download_missing_audio_frequency_hours,
            id="download_missing",
            next_run_time=datetime.now(tz=timezone.utc),
        )


def add_backup_tasks(scheduler: AsyncIOScheduler):
    config = get_config().backups

    if config.lite_frequency_days > 0:
        scheduler.add_job(
            lite_backup_task,
            "interval",
            days=config.lite_frequency_days,
            id="lite_backup",
        )

    if config.full_frequency_days > 0:
        scheduler.add_job(
            full_backup_task,
            "interval",
            days=config.full_frequency_days,
            id="full_backup",
        )

    if config.trim_frequency_days > 0:
        scheduler.add_job(
            trim_backups_task,
            "interval",
            days=config.trim_frequency_days,
            id="trim_backups",
        )


def start_automated_tasks():
    config = get_config()
    scheduler = AsyncIOScheduler()

    if config.backups.enabled:
        add_backup_tasks(scheduler)

    if config.automated.enabled:
        add_automated_tasks(scheduler)

    return scheduler
