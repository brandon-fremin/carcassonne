from websockets.server import WebSocketServerProtocol
from websockets.typing import Data
from src.websocketserver.serverstate import ServerState
from src.proto import carcassonne_pb2
from google.protobuf.json_format import MessageToJson
from src.proto import carcassonne_proto

def handle_message(state: ServerState, connection_id: str, data: Data) -> None:
    message = carcassonne_pb2.Message()
    message.ParseFromString(data)
    mess = MessageToJson(message, including_default_value_fields=True)
    print(f"Message from [{type(data)}] {connection_id}: {data} --- {mess}")

    carcassonne_proto.Message().from_bytes(data)

    state.num_messages += 1