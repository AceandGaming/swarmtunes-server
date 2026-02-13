import os
from scripts.log import logger

CORS_ENABLED = os.getenv("CORS", "true").lower() == "true"

USER_MAX_PLAYLISTS = int(os.getenv("USER_MAX_PLAYLISTS", 30))
USER_MIN_PASSWORD_LENGTH = int(os.getenv("USER_MIN_PASSWORD_LENGTH", 8))
USER_MAX_PASSWORD_LENGTH = int(os.getenv("USER_MAX_PASSWORD_LENGTH", 128))
MAX_DELETED_FILES_SIZE = float(os.getenv("MAX_DELETED_FILES_SIZE", 2e8))
TOKEN_EXPIRATION_DAYS = int(os.getenv("TOKEN_EXPIRATION_DAYS", 30))
SESSION_EXPIRATION_HOURS = int(os.getenv("SESSION_EXPIRATION_HOURS", 12))

MAINTENACE_ENABLED = os.getenv("MAINTENANCE", "false").lower() == "true"
MAX_MAINTENACE_DOWNLOAD_PERCENT = float(os.getenv("MAX_MAINTENACE_DOWNLOAD_PERCENT", 1))
MAX_MAINTENACE_DELETE_PERCENT = float(os.getenv("MAX_MAINTENACE_DELETE_PERCENT", 0.1))
MAX_MAINTENACE_REPLACE_PERCENT = float(os.getenv("MAX_MAINTENACE_REPLACE_PERCENT", 0.2))
MAX_MAINTENACE_REDOWNLOAD_PERCENT = float(os.getenv("MAX_MAINTENACE_REDOWNLOAD_PERCENT", 0.4))
MAINTENANCE_CLEAR_RCLONE = os.getenv("MAINTENANCE_CLEAR_RCLONE", "false").lower() == "true"

def LogConfigs():
    text = ""
    for name, value in globals().items():
        if not name.startswith("__") and not callable(value) and not isinstance(value, type(os)):
            text += f"{name}: {value}\n"

    logger.debug(f"Config:\n{text}")

LogConfigs()