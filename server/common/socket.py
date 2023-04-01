import select
import socket

class Socket:
	def __init__(self, socket):
		self._socket = socket

	def recv(self, max_bytes):
		raw_msg = b''
		total_bytes_received = 0

		while total_bytes_received < max_bytes:
			partial_msg = self._socket.recv(max_bytes - total_bytes_received)
			raw_msg += partial_msg
			total_bytes_received += len(partial_msg)

		return raw_msg
		

	def send(self, msg):
		total_bytes_sent = 0

		while total_bytes_sent < len(msg):
			total_bytes_sent += self._socket.send(msg[total_bytes_sent:])

	def close(self):
		self._socket.close()

