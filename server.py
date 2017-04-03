import socket
import time

server_socket = socket.socket(socket.AF_INET, 
							  socket.SOCK_STREAM)

host = '127.0.0.1' # localhost
port = 51713

# bind to the port
server_socket.bind((host, port))

server_socket.listen(5)
print('waiting for connection...')

while True:
	client_socket, addr = server_socket.accept();
	# print type(addr)
	print addr
	# print("Got a connection from %s" % (socket.inet_ntoa(addr)))
	client_socket.send("Hi")
	client_socket.close()