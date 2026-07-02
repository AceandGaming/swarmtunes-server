from .cleanup import sync_cleanup
from .sync import sync


def sync_task():
    try:
        sync()
    except:
        raise
    finally:
        sync_cleanup()
