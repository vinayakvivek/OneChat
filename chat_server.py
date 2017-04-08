# chat_server.py
 
import sys, socket, select
import thread
from utils import *

HOST = 'localhost' 
PORT = 9009

SOCKET_LIST = []
SOCKET_NICK_MAP = []
RECV_BUFFER = 4096 

#####################
# Protocol :
# client -> server :
#       '\register' - client wants to register
#       '\login' - client wants to login
#       '\logout' - client wants to logout
# 
# server -> client :
#       1 - login/registration successful
#       0 - unsuccessful 
#####################

def send(client_socket, message):
    try:
        client_socket.send(message)
        return True
    except:
        # disconnect and remove broken socket
        client_socket.close()
        if client_socket in SOCKET_LIST:
            SOCKET_LIST.remove(client_socket)
        return False

def log_out(server_socket, client_socket, addr):
    broadcast(server_socket, client_socket, "\r" + "Client (%s, %s) is offline\n" % addr) 
    client_socket.close()
    if client_socket in SOCKET_LIST:
        SOCKET_LIST.remove(client_socket)

def client_thread(server_socket, client_socket, addr):
    
    while True:
        cmd = client_socket.recv(RECV_BUFFER).rstrip()
        if cmd == '\\register':
            # get username
            username = client_socket.recv(RECV_BUFFER).rstrip()
            password = client_socket.recv(RECV_BUFFER).rstrip()

            if not check_username(username):
                new_user(username, password)
                send(client_socket, '1')
                break
            else:
                send(client_socket, 'Nick already taken!')

        elif cmd == '\\login':
            username = client_socket.recv(RECV_BUFFER).rstrip()
            password = client_socket.recv(RECV_BUFFER).rstrip()

            if check_credentials(username, password):
                print(client_socket.getpeername(), ' joined!')
                send(client_socket, '1')
                SOCKET_LIST.append(client_socket)
                broadcast(server_socket, client_socket, "\r" + "Client (%s, %s) has joined the room\n" % addr) 
                break
            else:
                send(client_socket, '0')
                print('invalid username/pass')
        else:
            send(client_socket, 'Invalid command! try again')


# def log_in(server_socket, client_socket, addr):
#     i = 0
#     while True:
#         print(i)
#         i += 1
        
#         print('get username : ')
#         username = client_socket.recv(RECV_BUFFER).rstrip()
#         print(username)

#         print('get pass : ')
#         password = client_socket.recv(RECV_BUFFER).rstrip()
#         print(password)

#         if username == 'user' and password == 'pass':
#             print(client_socket.getpeername(), ' joined!')
#             send(client_socket, '1')
#             SOCKET_LIST.append(client_socket)
#             broadcast(server_socket, client_socket, "\r" + "Client (%s, %s) has joined the room\n" % addr) 
#             break
#         else:
#             send(client_socket, '0')
#             print('invalid username/pass')


def chat_server():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    print "Chat server started on port " + str(PORT)
 
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read, ready_to_write , in_error = select.select(SOCKET_LIST,[],[],1)
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                thread.start_new_thread(client_thread, (server_socket, sockfd, addr))
         
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        if data.rstrip() == '\\logout':
                            log_out(server_socket, sock, addr)
                            print('loggin out')
                        else:
                            # there is something in the socket
                            broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "\r" + "Client (%s, %s) is offline\n" % addr) 

                # exception 
                except:
                    broadcast(server_socket, sock, "\r" + "Client (%s, %s) is offline\n" % addr)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    """
    sock : client socket to which message should not be send
    """
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            send(socket, message)
 

if __name__ == "__main__":
    sys.exit(chat_server())


         