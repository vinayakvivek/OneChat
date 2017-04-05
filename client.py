import socket

BUFFER_SIZE = 100

s = socket.socket(socket.AF_INET, 
				  socket.SOCK_STREAM)

host = 'localhost'
port = 9010

# ip = socket.inet_aton('127.0.0.2')
# print socket.inet_ntoa(ip)

# s.bind(('127.0.0.1', 32345))
s.connect((host, port))

ack_msg = s.recv(BUFFER_SIZE)
print('server : %s' % (ack_msg))

if ack_msg:
	while True:
		data = raw_input('client : ')
		s.send(data)
		if data == 'q':
			break
		data = s.recv(BUFFER_SIZE)
		print('server : %s' % (data))

	s.recv(BUFFER_SIZE)
	print('server : %s' % (data))

s.close()