from scripts.download import *
from scripts.paths import *
from scripts.classes.song import SongManager
import os
import scripts.api.google_drive as google_drive


SongManager.Load()
song = SongManager.GetSong("8be2573a-e99a-4c02-bad4-cb6ca591c34d")
ReDownloadSong(song)