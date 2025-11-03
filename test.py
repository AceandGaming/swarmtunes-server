import os
#os.environ["DATA_PATH"] = "dev"
from scripts.download import *
from scripts.classes.user import UserManager, Admin, PlaylistManager
from scripts.classes.song import SongManager
from scripts.paths import *
import asyncio

