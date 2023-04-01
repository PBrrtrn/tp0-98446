def receive_int(socket):
	int_bytes = socket.recv(4)
	return int.from_bytes(int_bytes, 'big')

def receive_string(socket, string_len):
	raw_string = socket.recv(string_len)
	return raw_string.decode('utf-8')