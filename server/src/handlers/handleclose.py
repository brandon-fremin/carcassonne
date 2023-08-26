from src.websocketserver.serverstate import  ServerState
from typing import Union

def handle_close(state: ServerState, connection_id: str) -> Union[str, None]:
    if connection_id in state.connections.keys():
        del state.connections[connection_id]
        print(f"Closed with {connection_id}")
        return connection_id
    else:
        print(f"No existing connection with {connection_id}")
        return None
    