import socket

s = socket.socket(socket.AF_INET, 
				  socket.SOCK_STREAM)

host = 'localhost'
port = 51713

# ip = socket.inet_aton('127.0.0.2')
# print socket.inet_ntoa(ip)

s.bind(('127.0.0.1', 32345))
s.connect((host, port))

msg = s.recv(1024)

s.close()

print('server : %s' % (msg))