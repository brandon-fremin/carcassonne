from typing import Callable
import logging, json, traceback, time
from src.httpcontext import HttpContext
from clients.lionelclient import LionelClient
from clients.cassandraclient import CassandraClient
from clients.lokiclient import GLOBAL_LOKI_CLIENT
from functools import wraps
from threading import Thread
from datetime import datetime
from common.utils import synchronized

logger = logging.getLogger(__name__)


def http_middleware(func):
    @wraps(func)
    def wrapper(self, request: dict) -> dict:
        start = time.perf_counter()
        response = { "error": {} }
        try:
            request_str = json.dumps(request)
            logger.info(f"HTTP func={func.__name__} size={len(request_str)}B request={request_str}")
            response = func(self, request)
        except Exception as e:
            response = {
                "error": {
                    "message": str(e),
                    "type": str(type(e)),
                    "stacktrace": traceback.format_exc()
                }
            }
        elapsed_sec = time.perf_counter() - start
        response_str = json.dumps(response)
        response_size = len(response_str)
        if len(response_str) > 1000:
            response_str = response_str[:1000] + f" ... [shortened from {response_size} chars]"
        logger.info(f"HTTP func={func.__name__} elapsedSec={elapsed_sec:0.3f} size={response_size}B response={response_str}")
        return response
    return wrapper


class HandlerHeartbeat:
    def __init__(self, ws_send: Callable[[str, dict], None], health: Callable[[], dict]):
        self._ws_send = ws_send
        self._connection_ids: list[str] = []
        self._thread = Thread(target=self._run, daemon=True)
        self._health = health
        self._heartbeat_interval_sec = 60

    def start(self):
        self._thread.start()

    @synchronized
    def add_connection(self, connection_id: str) -> None:
        self._connection_ids.append(connection_id)

    @synchronized
    def remove_connection(self, connection_id: str) -> None:
        self._connection_ids.remove(connection_id)

    @synchronized
    def send(self, connection_id: str | None = None) -> None:
        message = {
            "heartbeat": {
                "now": datetime.now().isoformat(),
                "health": self._health()
            }
        }
        if connection_id:
            self._ws_send(connection_id, message)
        else:
            for conn_id in self._connection_ids:
                self._ws_send(conn_id, message)

    def _run(self) -> None:
        while True:
            self.send()
            time.sleep(self._heartbeat_interval_sec)

class Handler:
    def __init__(self, ws_send: Callable[[str, dict], None]):
        self._ws_send = ws_send
        self._lionel_client = LionelClient()
        self._cassandra_client = CassandraClient("cassandra", "cassandra")
        self._heartbeat = HandlerHeartbeat(self.send, self._health)

    def _health(self) -> dict:
        return {
            "cassandra": "OK" if self._cassandra_client.is_available() else "FAIL",
            "loki": "OK" if GLOBAL_LOKI_CLIENT.is_available() else "FAIL",
            "train": "FAIL",
            "lionel": "FAIL",
        }

    def noop_connect(self, context: HttpContext):
        self._heartbeat.add_connection(context.ray)
        self._heartbeat.send()
        logger.info(f"WS CONNECT {context=}")

    def noop_disconnect(self, context: HttpContext):
        self._heartbeat.remove_connection(context.ray)
        logger.info(f"WS DISCONNECT {context=}")

    def send(self, connection_id: str, message: dict):
        logger.info(f"WS SEND {connection_id=}")
        self._ws_send(connection_id, message)

    def ws_ping(self, context: HttpContext, message: dict):
        logger.info(f"WS RECV {context=}")
        self.send(
            context.ray,
            {"status": "ok", "message": "Server is running", "data": message},
        )

    @http_middleware
    def http_ping(self, request: dict) -> dict:
        return {"status": "ok", "message": "Server is running", "data": request}

    @http_middleware
    def http_lionel(self, request: dict) -> dict:
        response = {
            "ZACCDATA": [],
            "ZPAGEDATA": [],
            "ZTRACKDATA": [],
            "ZPOWERDATA": []
        }
        for table in response.keys():
            response[table] = self._lionel_client.read_table(table)

        response["svg"] = {}
        # with open("lionel/tracks/straight.svg", "r") as f:
        #     response["svg"][1] = f.read()
        # with open("lionel/tracks/curve381.svg", "r") as f:
        #     response["svg"][4] = f.read()
        # with open("lionel/tracks/short.svg", "r") as f:
        #     response["svg"][6] = f.read()
        return response