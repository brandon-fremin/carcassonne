from websockets.server import WebSocketServerProtocol
from typing import Dict

class Connection:
    websocket: WebSocketServerProtocol

    def __init__(self, websocket: WebSocketServerProtocol): 
        self.websocket = websocket

    def __str__(self):
        return str({
            "id": self.uuid(),
            "remote_address": self.websocket.remote_address,
            "latency": self.websocket.latency
        })

    def uuid(self) -> str:
        return self.websocket.id.hex

class ServerState:
    connections: Dict[str, Connection]
    address: str
    port: int
    num_messages: int

    def __init__(self, address="localhost", port=8765):
        self.connections = {}
        self.tasks = {}
        self.num_messages = 0
        self.address = address
        self.port = port

    def metrics(self):
        return {
            "num_messages": self.num_messages,
            "num_connections": len(self.connections)
        }