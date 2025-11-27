from fastapi import WebSocket
import json, threading, logging, asyncio
from queue import Queue
from collections import defaultdict
from typing import Callable


logger = logging.getLogger(__name__)


class SocketPool:
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._rooms: dict[str, set[str]] = defaultdict(set)
        self._message_queue: Queue[tuple[str, dict, threading.Event]] = Queue()
        self._message_task: asyncio.Task = None

    def add(self, connection_id: str, room_id: str, websocket: WebSocket) -> str:
        self._connections[connection_id] = websocket
        self._rooms[room_id].add(connection_id)
        return connection_id

    def remove(self, connection_id: str):
        del self._connections[connection_id]
        for room in self._rooms.values():
            room.remove(connection_id)

    def send(self, connection_id: str, message: dict):
        async def func():
            websocket = self._connections.get(connection_id)
            if websocket:
                await websocket.send_text(json.dumps(message))
        loop = asyncio.get_event_loop()  # the main event loop
        asyncio.run_coroutine_threadsafe(func(), loop)

    def broadcast(self, room_id: str, message: dict):
        for connection_id in self._rooms.get(room_id, []):
            self.send(connection_id, message)

    class Sender:
        def __init__(self, send: Callable[[str, dict], None], broadcast: Callable[[str, dict], None]):
            self._send = send
            self._broadcast = broadcast
        
        def send(self, connection_id: str, message: dict):
            self._send(connection_id, message)

        def broadcast(self, room_id: str, message: dict):
            self._broadcast(room_id, message)

    def sender(self) -> Sender:
        return SocketPool.Sender(self.send, self.broadcast)