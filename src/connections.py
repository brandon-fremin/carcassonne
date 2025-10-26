from fastapi import WebSocket
import json, threading
import uuid, asyncio
from queue import Queue


class Connections:
    def __init__(self):
        self._connections: dict[str, WebSocket] = {}
        self._message_queue: Queue[tuple[str, dict, threading.Event]] = Queue()
        self._message_task: asyncio.Task = None
        self._thread = threading.Thread(
            target=asyncio.run, args=(self._message_sender(),), daemon=True
        )

    def run(self):
        self._thread.start()

    def add(self, websocket: WebSocket) -> str:
        connection_id = str(uuid.uuid4())
        self._connections[connection_id] = websocket
        return connection_id

    def remove(self, connection_id: str):
        del self._connections[connection_id]

    def send(self, connection_id: str, message: dict):
        event = threading.Event()
        self._message_queue.put((connection_id, message, event))
        event.wait()  # wait until message is sent

    async def _message_sender(self):
        while True:
            # block and wait for a message
            connection_id, message, event = self._message_queue.get()
            websocket = self._connections.get(connection_id)
            if websocket:
                await websocket.send_text(json.dumps(message))
            event.set()
