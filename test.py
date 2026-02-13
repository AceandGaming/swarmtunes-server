from scripts.log import logger
from scripts.id_manager import IDManager
from scripts.types import *
from scripts.api.rclone_api import *
import random
from scripts.data_system import DataSystem
import acoustid
import scripts.paths as paths

IDManager.Load()