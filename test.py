from scripts.id_manager import IDManager
from scripts.types import *
from scripts.serializer import *
from scripts.types.song import SongExternalStorage
from scripts.types.user import UserData
from scripts.data_system import DataSystem
from scripts.download import *
from scripts.api.google_drive import *
import scripts.paths as paths
from datetime import datetime
import json
from pathlib import Path
import os
from scripts.search import *
import time
import scripts.maintenance as maintenance
from scripts.delete import DeleteManager
from scripts.load_metadata import *

IDManager.Load()

DeleteManager.RecoverDeleted(DeleteManager.LoadDeleted("2025-12-22T10:56:20.372852"))