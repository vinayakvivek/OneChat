# chat_server.py
 
import sys, socket, select
import thread
 
def someFunc():
    print "someFunc was called"
 
# thread.start_new_thread(someFunc, ())

HOST = 'localhost' 
SOCKET_LIST = []
RECV_BUFFER = 4096 
PORT = 9009

def log_in(server_socket, cliet_socket):
    i = 0
    while True:
        print(i)
        i += 1
        
        print('get username : ')
        username = cliet_socket.recv(RECV_BUFFER).rstrip()
        print(username)

        print('get pass : ')
        password = cliet_socket.recv(RECV_BUFFER).rstrip()
        print(password)

        if username == 'user' and password == 'pass':
            print(cliet_socket.getpeername(), ' joined!')
            cliet_socket.send('1')
            SOCKET_LIST.append(cliet_socket)
            break
        else:
            cliet_socket.send('0')
            print('invalid username/pass')


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
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[],1)

        # print('SOCKET_LIST : ', SOCKET_LIST)
        print(ready_to_read, ready_to_write, in_error)
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                thread.start_new_thread(log_in, (server_socket, sockfd))

                # # get username
                # username = sockfd.recv(RECV_BUFFER)

                # # get password
                # password = sockfd.recv(RECV_BUFFER)

                # print((username.rstrip()), (password.rstrip()))

                # if log_in(username.rstrip(), password.rstrip()):
                #     print "Client (%s, %s) connected" % addr
                #     sockfd.send('1')
                #     broadcast(server_socket, sockfd, "[%s:%s] entered our chatting room\n" % addr)
                # else:
                #     sockfd.send('0')
                #     SOCKET_LIST.remove(sockfd)
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # there is something in the socket
                        broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr) 

                # exception 
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":

    sys.exit(chat_server())


         