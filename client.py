import socket

buffer_size = 100

s = socket.socket(socket.AF_INET, 
				  socket.SOCK_STREAM)

host = 'localhost'
port = 51714

# ip = socket.inet_aton('127.0.0.2')
# print socket.inet_ntoa(ip)

s.bind(('127.0.0.1', 32345))
s.connect((host, port))

# s.send('Hi pls send me the file!')

file_data = ''

while True:
	data = s.recv(buffer_size)
	if not data:
		break

	print('recieved data : %s' % data)
	file_data += data


print(file_data)
s.close()
