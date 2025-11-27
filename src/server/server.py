from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
import uvicorn
import json, logging
from typing import Callable
from functools import wraps, partial
from urllib.parse import unquote

from src.server.socketpool import SocketPool
from src.common.httpcontext import HttpContext
from src.common.lokilogger import GLOBAL_LOKI_CLIENT
from src.clients.grafanaclient import GLOBAL_GRAFANA_CLIENT
from src.server.heartbeat import Heartbeat
from src.clients.lionelclient import LionelClient
from src.clients.cassandraclient import CassandraClient
from src.common import constants

from src.handlers.handle_iam import handle_iam
from src.handlers.handle_ping import handle_ping
from src.handlers.handle_get_preview import handle_get_preview

from src.handlers.handle_get_track import handle_get_track
from src.handlers.handle_create_track import handle_create_track
from src.handlers.handle_delete_track import handle_delete_track

from src.handlers.handle_get_layout import handle_get_layout
from src.handlers.handle_create_layout import handle_create_layout
from src.handlers.handle_delete_layout import handle_delete_layout
from src.handlers.handle_put_layout import handle_put_layout

logger = logging.getLogger("server")


_PUT_REGISTRY: dict[str, Callable] = {}
_DELETE_REGISTRY: dict[str, Callable] = {}
_POST_REGISTRY: dict[str, Callable] = {}
_GET_REGISTRY: dict[str, Callable] = {}
_WS_REGISTRY: dict[str, Callable] = {}


def __register(route: str, registry: dict[str, Callable]):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        registry[route] = func
        return wrapper

    return decorator


def get(route: str):
    return __register(route, _GET_REGISTRY)


def post(route: str):
    return __register(route, _POST_REGISTRY)

def put(route: str):
    return __register(route, _PUT_REGISTRY)

def delete(route: str):
    return __register(route, _DELETE_REGISTRY)


def websocket(route: str):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(self, *args, **kwargs)

        _WS_REGISTRY[route] = func
        return wrapper

    return decorator


def parse_url_params(request: Request) -> dict:
    req = {}
    for key, value in request.query_params.items():
        val = unquote(value)
        try:
            val = json.loads(val)
        except json.JSONDecodeError:
            pass
        req[key] = val
    return req


async def parse_http_request(request: Request) -> tuple[dict, HttpContext]:
    context = HttpContext(request.headers)
    logging.info(f"Received HTTP request {context=}")
    req = Server.parse_bytes(await request.body())
    if request.method in ["GET", "DELETE"]:
        req = parse_url_params(request)
    return (req, context)


class Server:
    def __init__(self, log_level="info"):
        self._app = FastAPI()
        self._host = constants.SERVER_HOST
        self._port = constants.SERVER_PORT
        self._log_level = log_level
        self._connections = SocketPool()
        self._lionel_client = LionelClient()
        self._cassandra_client = CassandraClient("cassandra", "cassandra")
        self._heartbeat = Heartbeat(self.health, 60)
        for route, func in _GET_REGISTRY.items():
            self._app.get(route)(partial(func, self))
        for route, func in _POST_REGISTRY.items():
            self._app.post(route)(partial(func, self))
        for route, func in _DELETE_REGISTRY.items():
            self._app.delete(route)(partial(func, self))
        for route, func in _PUT_REGISTRY.items():
            self._app.put(route)(partial(func, self))
        for route, func in _WS_REGISTRY.items():
            self._app.websocket(route)(partial(func, self))

    def run(self):
        logger.info("Starting server...")
        uvicorn.run(
            self._app, host=self._host, port=self._port, log_level=self._log_level
        )

    @staticmethod
    def parse_bytes(raw_request: bytes) -> dict:
        body: str = raw_request.decode()
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return {"text": body}

    @get("/api/ping")
    async def api_ping(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_ping(req))

    @get("/api/iam")
    async def api_iam(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_iam(ctx))

    @get("/api/preview")
    async def api_get_preview(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_get_preview(req))

    @post("/api/track")
    async def api_post_track(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_create_track(req, ctx, self._cassandra_client))
    
    @delete("/api/track")
    async def api_delete_track(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_delete_track(req, self._cassandra_client))

    @get("/api/track")
    async def api_get_track(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_get_track(req, self._cassandra_client))

    @post("/api/layout")
    async def api_post_layout(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_create_layout(req, ctx, self._cassandra_client))

    @put("/api/layout")
    async def api_put_layout(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_put_layout(req, ctx, self._cassandra_client))

    @get("/api/layout")
    async def api_get_layout(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_get_layout(req, self._cassandra_client))

    @delete("/api/layout")
    async def api_delete_layout(self, request: Request) -> JSONResponse:
        (req, ctx) = await parse_http_request(request)
        return JSONResponse(content=handle_delete_layout(req, self._cassandra_client))

    @websocket("/api/ws/{room_id}")
    async def api_websocket(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        context = HttpContext(websocket.headers)
        logging.info(f"Received WebSocket connection {context=}")
        self._connections.add(context.ray, room_id, websocket)
        self.health()
        try:
            while True:
                message = Server.parse_bytes((await websocket.receive_text()).encode())
                self.on_message(message, context, room_id)
        finally:
            self._connections.remove(context.ray)

    def on_message(self, message: dict, context: HttpContext, room_id: str):
        if "heartbeat" in message:
            self._connections.send(
                context.ray,
                {
                    "status": "ok",
                    "message": "Server is running",
                    "roomId": room_id,
                    "data": message,
                },
            )

    def health(self):
        message = {
            "heartbeat": {
                "cassandra": "OK" if self._cassandra_client.is_available() else "FAIL",
                "loki": "OK" if GLOBAL_LOKI_CLIENT.is_available() else "FAIL",
                "grafana": "OK" if GLOBAL_GRAFANA_CLIENT.is_available() else "FAIL",
                "train": "FAIL",
                "lionel": "FAIL",
            }
        }
        self._connections.broadcast("heartbeat", message)
