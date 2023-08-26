from src.websocketserver.serverstate import ServerState
from typing import Union
import copy, asyncio

def handle_dump_metrics(state: ServerState) -> Union[str, None]:
    print(f"Metrics: {state.metrics()}")
    callback = lambda: handle_dump_metrics(state)
    asyncio.get_running_loop().call_later(15, callback) 