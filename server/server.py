import asyncio

from src.websocketserver.websocketserver import WebSocketServer

# from src.proto.carcassonne_pb2 import Message
# from google.protobuf.json_format import MessageToJson

# message = Message()
# message.sender.type = 1
# message.sender.id = "abcdef"
# message.payload.echoRequest.data = "Hello"

# print(type_pb2(message))
# print(message.payload.WhichOneof('payload'))
# print(MessageToJson(message, including_default_value_fields=True))
# print(message.MessageToJson())

async def main():
    server = WebSocketServer(address="localhost", port=8765)
    await server.run()

asyncio.run(main())
