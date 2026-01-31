from scripts.log import logger
from scripts.id_manager import IDManager
from scripts.types import *
from scripts.api.rclone_api import *
import scripts.maintenance as maintenance

IDManager.Load()

for i in range(10):
    files = GetAllFiles()
    print(len(files))