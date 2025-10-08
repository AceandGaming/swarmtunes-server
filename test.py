from scripts.download import *
from scripts.paths import *
from scripts.classes.song import SongManager
import os
import scripts.api.google_drive as google_drive


SongManager.Load()
asyncio.run(DownloadMissingSongs())