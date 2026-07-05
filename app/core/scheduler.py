from apscheduler.schedulers.asyncio import AsyncIOScheduler

from automated.tasks import song_sync_task
from core.config import get_config


def start_automated_tasks():
    config = get_config()
    scheduler = AsyncIOScheduler()

    if not config.automated.enabled:
        return scheduler

    scheduler.add_job(
        song_sync_task, "interval", hours=config.automated.frequency_hours, id="song_sync"
    )

    return scheduler
