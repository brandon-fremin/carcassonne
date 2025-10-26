from typing import Callable
import logging, json

logger = logging.getLogger(__name__)


class Handler:
    def __init__(self, ws_send: Callable[[str, dict], None]):
        self._ws_send = ws_send

    def noop_connect(self, connection_id: str):
        logger.info(f"WS CONNECT connection={connection_id}")

    def noop_disconnect(self, connection_id: str):
        logger.info(f"WS DISCONNECT connection={connection_id}")

    def send(self, connection_id: str, message: dict):
        logger.info(f"WS SEND connection={connection_id} message={json.dumps(message)}")
        self._ws_send(connection_id, message)

    def ws_ping(self, connection_id: str, message: dict):
        logger.info(f"WS RECV connection={connection_id} message={json.dumps(message)}")
        self.send(
            connection_id,
            {"status": "ok", "message": "Server is running", "data": message},
        )

    def http_ping(self, request: dict) -> dict:
        logger.info(f"HTTP request={json.dumps(request)}")
        response = {"status": "ok", "message": "Server is running", "data": request}
        logger.info(f"HTTP response={json.dumps(response)}")
        return response
