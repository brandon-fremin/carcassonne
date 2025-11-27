import colorama

colorama.just_fix_windows_console()

import logging, threading
from queue import Queue
from datetime import datetime
from zoneinfo import ZoneInfo

from src.clients.lokiclient import LokiRecord, GLOBAL_LOKI_CLIENT
from src.common import constants

class _LokiHandler(logging.Handler):
    def __init__(
        self,
        level=logging.NOTSET,
    ):
        self._batch_size = max(constants.LOKI_BATCH_SIZE, 1)
        self._queue: Queue[logging.LogRecord] = Queue()
        self._thread = threading.Thread(target=self._process_logs, daemon=True)
        super().__init__(level)
        self._thread.start()

    def emit(self, record):
        self._queue.put(record)

    def _process_logs(self):
        while True:
            record = self._queue.get()
            batch = [record]
            while len(batch) < self._batch_size and not self._queue.empty():
                batch.append(self._queue.get(block=False))
            GLOBAL_LOKI_CLIENT.send([_LokiHandler._make_loki_record(r) for r in batch])

    @staticmethod
    def _make_loki_record(record: logging.LogRecord) -> LokiRecord:
        tz = ZoneInfo(constants.TZ)
        timestamp = datetime.fromtimestamp(record.created).astimezone(tz).isoformat()
        labels = {
            "ts": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "filename": record.filename,
            "lineno": str(record.lineno),
            "thread": str(record.thread),
            "host": constants.MACHINE_NAME,
            "job": constants.APP_NAME,
        }
        return LokiRecord(
            labels,
            int(record.created * 1e9),
            record.getMessage(),
        )


def _disable_url_loggers():
    """
    Disable loggers for 'urllib3' and 'requests' to prevent cluttering the output.
    """
    logger_dict = logging.root.manager.loggerDict.copy()
    disabled = []
    for logger_name, logger in logger_dict.items():
        if any(
            logger_name == name or logger_name.startswith(f"{name}.")
            for name in constants.DISABLED_LOGGERS
        ) and isinstance(logger, logging.Logger):
            disabled.append(logger_name)
            logger.setLevel(logging.CRITICAL + 1)
    if len(disabled) > 0:
        logging.info(f"Disabling loggers: {disabled}")


def configure_logging(level):
    logging.basicConfig(
        level=level,  # Set the desired logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format=constants.LOGGER_FORMAT,
        datefmt=constants.LOGGER_DATEFMT,
    )
    logging.getLogger().addHandler(_LokiHandler())
    _disable_url_loggers()
