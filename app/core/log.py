import logging
import os

levels = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR
}
level = levels.get(os.getenv("LOG_LEVEL", "INFO"), logging.INFO)

logging.basicConfig(
    level=level,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.FileHandler('server.log'), logging.StreamHandler()]
)

logger = logging.getLogger("Swarmtunes")
logger.info("---LOG START---")