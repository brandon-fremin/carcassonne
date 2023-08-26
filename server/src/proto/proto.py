class Proto:
	def from_bytes(self, data: bytes):
		# descriptor = protobuf.descriptor.Descriptor(self.__class__.__name__)
		message = protobuf.reflection.ParseMessage(self.__proto_descriptor__, data)
		mess = protobuf.json_format.MessageToJson(message, including_default_value_fields=True)
		print(mess)
