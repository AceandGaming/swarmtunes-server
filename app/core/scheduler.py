from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from automated.tasks import (
    delete_old_task,
    delete_orphaned_task,
    song_sync_task,
)
from core.config import get_config


def start_automated_tasks():
    config = get_config()
    scheduler = AsyncIOScheduler()

    if not config.automated.enabled:
        return scheduler

    if config.automated.sync_frequency_hours > 0:
        scheduler.add_job(
            song_sync_task,
            "interval",
            hours=config.automated.sync_frequency_hours,
            id="song_sync",
            next_run_time=datetime.now(tz=timezone.utc),
        )

    if config.automated.delete_old_frequency_hours > 0:
        scheduler.add_job(
            delete_old_task,
            "interval",
            hours=config.automated.delete_old_frequency_hours,
            id="delete_old",
            next_run_time=datetime.now(tz=timezone.utc),
        )

    if config.automated.delete_orphaned_frequency_hours > 0:
        scheduler.add_job(
            delete_orphaned_task,
            "interval",
            hours=config.automated.delete_orphaned_frequency_hours,
            id="delete_orphaned",
            next_run_time=datetime.now(tz=timezone.utc),
        )

    return scheduler
