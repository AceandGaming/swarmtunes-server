from scripts.log import logger
from scripts.id_manager import IDManager
from scripts.types import *
from scripts.api.rclone_api import *
import scripts.maintenance as maintenance

IDManager.Load()

print(IDManager.NewId(Song))