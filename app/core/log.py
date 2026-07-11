import json
import logging.config
from logging import LogRecord
from queue import Queue

from core.paths import CONFIG, LOGS

log_queue: Queue[LogRecord] = Queue()


class QueueLogHandler(logging.Handler):
    def emit(self, record):
        log_queue.put(record)


def setup_logging():
    with open(CONFIG / "log_config.json", "r") as f:
        dict = json.load(f)
        for handler in dict["handlers"].values():
            if "filename" not in handler:
                continue
            handler["filename"] = str(LOGS / handler["filename"])
        logging.config.dictConfig(dict)

        for name in dict["loggers"].keys():
            logger = logging.getLogger(name)
            logger.addHandler(QueueLogHandler())
