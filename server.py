import socket
import time

buffer_size = 100

server_socket = socket.socket(socket.AF_INET, 
							  socket.SOCK_STREAM)

host = '127.0.0.1' # localhost
port = 51714

# bind to the port
server_socket.bind((host, port))

server_socket.listen(5)
print('waiting for connection...')

while True:
	client_socket, addr = server_socket.accept();
	print("connected to %s" % (str(addr)))

	client_data = client_socket.recv(buffer_size)
	print('Data recieved by the server : %s' % (str(client_data)))

	f = open('random.txt', 'rb')
	line = f.read(buffer_size)
	while (line):
		client_socket.send(line)
		print('sent ', line)
		line = f.read(buffer_size)

	f.close()

	client_socket.send('connection terminating..')
	client_socket.close()