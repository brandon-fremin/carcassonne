import colorama

colorama.just_fix_windows_console()

import logging, sys, threading
from zoneinfo import ZoneInfo
from datetime import datetime
import requests, time, json
from queue import Queue
from src import constants


class LokiHandler(logging.Handler):
    def __init__(
        self,
        level=logging.NOTSET,
    ):
        self._loki_url = f"http://{constants.LOKI_HOST}:{constants.LOKI_PORT}"
        self._loki_is_available = False
        self._ping_timeout = constants.LOKI_PING_TIMEOUT
        self._batch_size = max(constants.LOKI_BATCH_SIZE, 1)
        self._queue: Queue[logging.LogRecord] = Queue()
        self._thread = threading.Thread(target=self._process_logs, daemon=True)
        super().__init__(level)
        self._thread.start()

    def emit(self, record):
        self._queue.put(record)

    def _process_logs(self):
        # datetime.fromtimestamp(record.created).astimezone(zoneinfo.ZoneInfo("America/New_York")).isoformat()
        while True:
            record = self._queue.get()
            batch = [record]
            while len(batch) < self._batch_size and not self._queue.empty():
                batch.append(self._queue.get(block=False))
            self._send_to_loki(batch)

    @staticmethod
    def _make_stream(record: logging.LogRecord) -> dict:
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
        return {
            "stream": labels,
            "values": [[str(int(record.created * 1e9)), record.getMessage()]],
        }

    def _send_to_loki(
        self,
        batch: list[logging.LogRecord],
        errors: list[requests.exceptions.RequestException] = None,
    ):
        if errors is None:
            errors = []
        if len(errors) >= 3:
            print(
                "Failed to send logs to Loki after 3 attempts. Dropping logs. errors:",
                errors,
            )
            return
        self._wait_for_loki()

        payload = {"streams": [LokiHandler._make_stream(record) for record in batch]}

        headers = {"Content-Type": "application/json"}

        try:
            resp = requests.post(
                f"{self._loki_url}/loki/api/v1/push",
                data=json.dumps(payload),
                headers=headers,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            self._loki_is_available = False
            errors.append(e)
            self._send_to_loki(batch, errors)

    def _wait_for_loki(self):
        while not self._loki_is_available:
            self._loki_is_available = self._ping_loki()
            if not self._loki_is_available:
                print(
                    f"Loki server is unreachable. Retrying in {self._ping_timeout} seconds..."
                )
                time.sleep(self._ping_timeout)

    def _ping_loki(self) -> bool:
        query = '{job!=""}'
        params = {"query": query, "limit": 1}
        try:
            response = requests.get(
                f"{self._loki_url}/loki/api/v1/query", params=params
            )
            response.raise_for_status()
            data: dict = response.json()
            return data.get("status") == "success"
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to Loki at {self._loki_url}: {e}")
        return False


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
        datefmt=constants.LOGGER_DATEFMT
    )
    logging.getLogger().addHandler(LokiHandler())
    _disable_url_loggers()
