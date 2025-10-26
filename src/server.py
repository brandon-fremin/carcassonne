from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
import uvicorn
import json, logging
from typing import Callable

from src.connections import Connections
from src.handler import Handler
from src import constants

logger = logging.getLogger("server")


class Server:
    def __init__(self, log_level="info"):
        self._app = FastAPI()
        self._host = constants.SERVER_HOST
        self._port = constants.SERVER_PORT
        self._log_level = log_level
        self._connections = Connections()
        self._handler = Handler(self.ws_send)
        self.setup_http_get_endpoint("/ping", self._handler.http_ping)
        self.setup_websocket_endpoint(
            "/ping",
            self._handler.noop_connect,
            self._handler.ws_ping,
            self._handler.noop_disconnect,
        )

    def run(self):
        logger.info("Starting server...")
        self._connections.run()
        uvicorn.run(
            self._app, host=self._host, port=self._port, log_level=self._log_level
        )

    def setup_http_get_endpoint(self, route: str, handler: Callable[[dict], dict]):
        async def endpoint(request: Request) -> JSONResponse:
            body: str = (await request.body()).decode()
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                data = {"message": body}
            return JSONResponse(content=handler(data))

        self._app.get(route)(endpoint)

    def setup_websocket_endpoint(
        self,
        route: str,
        on_connect: Callable[[str], None],
        on_message: Callable[[str, dict], None],
        on_disconnect: Callable[[str], None],
    ):
        async def endpoint(websocket: WebSocket):
            await websocket.accept()
            connection_id = self._connections.add(websocket)
            on_connect(connection_id)
            try:
                while True:
                    body = await websocket.receive_text()
                    try:
                        data = json.loads(body)
                    except json.JSONDecodeError:
                        data = {"message": body}
                    on_message(connection_id, data)
            except WebSocketDisconnect:
                pass
            self._connections.remove(connection_id)
            on_disconnect(connection_id)

        self._app.websocket(route)(endpoint)

    def ws_send(self, connection_id: str, message: dict):
        self._connections.send(connection_id, message)
