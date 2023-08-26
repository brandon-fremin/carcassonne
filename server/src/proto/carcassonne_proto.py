from enum import Enum
from typing import List
from google import protobuf
from src.proto import carcassonne_pb2

class Proto:
	def from_bytes(self, data: bytes):
		# descriptor = protobuf.descriptor.Descriptor(self.__class__.__name__)
		message = protobuf.reflection.ParseMessage(self.__proto_descriptor__, data)
		mess = protobuf.json_format.MessageToJson(message, including_default_value_fields=True)
		print(mess)

class SenderType(Enum):
	ANONYMOUS = 0
	PLAYER = 1
	SERVER = 2
	DEVELOPER = 3

class Sender(Proto):
	type: SenderType
	id: str
	
	__proto_descriptor__ = carcassonne_pb2.Sender.DESCRIPTOR

class EchoRequest(Proto):
	data: str
	
	__proto_descriptor__ = carcassonne_pb2.EchoRequest.DESCRIPTOR

class EchoResponse(Proto):
	data: str
	
	__proto_descriptor__ = carcassonne_pb2.EchoResponse.DESCRIPTOR

class StartGameRequest(Proto):
	numPlayers: int
	playerNames: List[str]
	
	__proto_descriptor__ = carcassonne_pb2.StartGameRequest.DESCRIPTOR

class StartGameResponse(Proto):
	gameId: str
	
	__proto_descriptor__ = carcassonne_pb2.StartGameResponse.DESCRIPTOR

class Payload(Proto):
	class Choice:
		echoRequest: EchoRequest
		echoResponse: EchoResponse
		startGameRequest: StartGameRequest
		startGameResponse: StartGameResponse
	
	payload: Choice
	
	__proto_descriptor__ = carcassonne_pb2.Payload.DESCRIPTOR

class Message(Proto):
	sender: Sender
	payload: Payload
	
	__proto_descriptor__ = carcassonne_pb2.Message.DESCRIPTOR