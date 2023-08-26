from websockets.server import WebSocketServerProtocol
from src.websocketserver.serverstate import Connection, ServerState
from typing import Union

def handle_open(state: ServerState, websocket: WebSocketServerProtocol) -> str:
    connection = Connection(websocket)
    if connection.uuid() in state.connections.keys():
        raise Exception(f"Already connected to {connection}")
    
    state.connections[connection.uuid()] = connection
    print(f"Connection from {connection}")
    return connection.uuid()