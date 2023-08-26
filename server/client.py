import asyncio

from websockets.sync.client import connect

from src.proto import carcassonne_pb2

def hello():
    with  connect("ws://localhost:8765") as websocket:
        message = carcassonne_pb2.Message()
        message.sender.type = carcassonne_pb2.SenderType.PLAYER
        message.sender.id = "Brandon"
        message.payload.echoRequest.data = "Hello"
        data = message.SerializeToString()
        print(f"Message from [{type(data)}]: {data}")
        websocket.send(data)
        # message = websocket.recv()
        # print(f"Message from [{type(message)}]: {message}")

hello()