import logging, requests

logger = logging.getLogger(__name__)


class GrafanaClient:
    def __init__(self, url: str, username: str, password: str):
        self._url = url
        self._username = username
        self._password = password

    def is_available(self):
        res = requests.get(f"{self._url}/api/health", auth=(self._username, self._password))
        return res.status_code == 200


GLOBAL_GRAFANA_CLIENT = GrafanaClient("http://localhost:3000", "admin", "admin")