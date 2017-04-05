import socket
import time

BUFFER_SIZE = 100

server_socket = socket.socket(socket.AF_INET, 
							  socket.SOCK_STREAM)

host = '127.0.0.1' # localhost
port = 51713

# bind to the port
server_socket.bind((host, port))

server_socket.listen(5)
print('waiting for connection...')

while True:
	print('here1')
	client_socket, addr = server_socket.accept();
	client_socket.send('Hi !!')

	# print('here2')

	while True:
		data = client_socket.recv(BUFFER_SIZE)
		if data == 'q':
			break

		print('client : %s' % (data))

		data = raw_input('server : ')
		client_socket.send(data)

	client_socket.send('bye')
	client_socket.close()

	break