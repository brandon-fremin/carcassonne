import requests, time, json, logging

from src.common import constants
from src.common.utils import synchronized


logger = logging.getLogger(__name__)


class LokiRecord:
    def __init__(self, labels: dict, timestamp_ns: int, line: str):
        self.labels = labels
        self.timestamp_ns = str(timestamp_ns)
        self.line = line


class LokiClient:
    def __init__(self, url: str):
        self._url = url
        self._is_available = False
        self._ping_timeout = constants.LOKI_PING_TIMEOUT

    def send(self, records: list[LokiRecord], attempts: int = 3) -> None:
        if attempts <= 0:
            return print("Failed to send logs to Loki after 3 attempts. Dropping logs.")
        self._wait()

        payload = {
            "streams": [
                {
                    "stream": record.labels,
                    "values": [[record.timestamp_ns, record.line]],
                }
                for record in records
            ]
        }

        headers = {"Content-Type": "application/json"}

        try:
            resp = requests.post(
                f"{self._url}/loki/api/v1/push",
                data=json.dumps(payload),
                headers=headers,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            self.send(records, attempts - 1)

    @synchronized
    def is_available(self) -> bool:
        print("Adfadfadfadf")
        if not self._is_available:
            self._is_available = self._ping()
        if self._is_available:
            logger.info(f"Loki is reachable")
        return self._is_available

    @synchronized
    def _wait(self) -> None:
        while not self._is_available:
            self._is_available = self._ping()
            if not self._is_available:
                print(
                    f"Loki server is unreachable at {self._url}. Retrying in {self._ping_timeout} seconds..."
                )
                time.sleep(self._ping_timeout)

    def _ping(self) -> bool:
        query = '{job!=""}'
        params = {"query": query, "limit": 1}
        try:
            response = requests.get(f"{self._url}/loki/api/v1/query", params=params)
            response.raise_for_status()
            data: dict = response.json()
            return data.get("status") == "success"
        except requests.exceptions.RequestException as e:
            print(f"Failed to connect to Loki at {self._url}: {e}")
        return False


GLOBAL_LOKI_CLIENT = LokiClient(f"http://{constants.LOKI_HOST}:{constants.LOKI_PORT}")

