import asyncio, copy, contextlib, threading
from websockets.server import serve, WebSocketServerProtocol
from src.websocketserver.serverstate import ServerState

from src.handlers.handleopen import handle_open
from src.handlers.handlemessage import handle_message
from src.handlers.handleclose import handle_close
from src.handlers.handledumpmetrics import handle_dump_metrics

class WebSocketServer:
    state: ServerState
    lock: threading.Lock

    def __init__(self, address="localhost", port=8765):
        self.state = ServerState(address, port)
        self.lock = threading.Lock()

    async def run(self):
        async with serve(self.ws_handler, self.state.address, self.state.port):
            print("Ready to server")
            handle_dump_metrics(self.state)
            await asyncio.Future()  # run forever

    async def ws_handler(self, websocket: WebSocketServerProtocol) -> None:
        try:
            with self.lock:
                connection_id = handle_open(self.state, websocket)
            
            async for message in websocket:
                with self.lock:
                    handle_message(self.state, connection_id, message)
            
            with self.lock:
                handle_close(self.state, connection_id)       
        except Exception as e:
            print(f"Exception: {str(e)}")
            raise e
