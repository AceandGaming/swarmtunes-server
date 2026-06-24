import logging
import os
from logging.handlers import RotatingFileHandler
from core.paths import LOGS

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

level = LOG_LEVELS.get(os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

LOGS.mkdir(parents=True, exist_ok=True)
log_file = LOGS / "server.log"

formatter = logging.Formatter(
    "%(asctime)s %(funcName)s:%(lineno)d @%(name)s [%(levelname)s]: %(message)s",
    "%Y-%m-%d %H:%M:%S",
)

file_handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8",
)
file_handler.setFormatter(formatter)
file_handler.setLevel(level)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(level)


# Attach file logging to root (this is the key trick)
root_logger = logging.getLogger()
root_logger.setLevel(level)
root_logger.addHandler(file_handler)


root_logger.addHandler(console_handler)