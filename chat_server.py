# chat_server.py
 
import sys, socket, select
import thread
from utils import *
import json
# database
import sqlite3

#########################################
# LDAP

import ldap

ldap_conn = ldap.initialize('ldap://cs252lab.cse.iitb.ac.in:389/')
base_dn = "dc=cs252lab,dc=cse,dc=iitb,dc=ac,dc=in"

#########################################

conn = sqlite3.connect('onechat-test.db', check_same_thread=False)
c = conn.cursor()

QUERY_CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        dest TEXT NOT NULL,
        message TEXT
    );
'''

# Create table
c.execute(QUERY_CREATE_TABLE)

def save_message(source, dest, message):
    """
    saves message in the database
    format : <id>,<source>,<dest>,<message>
    """

    # Insert a row of data
    t = (source, dest, message, )
    c.execute("INSERT INTO messages (source, dest, message) VALUES (?, ?, ?)", t)

    # commit changes
    conn.commit()

def show_database():
    pass

#########################################

SOCKET_LIST = []
SOCKET_NICK_MAP = [] # list of tuples of the form (socket, username)
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
#       0 - invalid credentials
#       2 - Already logged in
#####################

def get_username(client_socket):
    """
    return : username linked to client_socket
    """
    for s in SOCKET_NICK_MAP:
        if s[0] == client_socket:
            return s[1]

    return None

def get_socket(username):
    """
    return : client socket linked to username
    """
    for s in SOCKET_NICK_MAP:
        if s[1] == username:
            return s[0]

    return None

def is_already_logged_in(username):
    """
    return: True if the user is already logged in
    """
    for s in SOCKET_NICK_MAP:
        if s[1] == username:
            return True
    return False

def disconnect_socket(client_socket):
    client_socket.close()
    
    # remove from SOCKET_LIST
    if client_socket in SOCKET_LIST:
        SOCKET_LIST.remove(client_socket)

    # remove from SOCKET_NICK_MAP
    for s in SOCKET_NICK_MAP:
        if s[0] == client_socket:
            SOCKET_NICK_MAP.remove(s)
            break

def add_socket(client_socket, username):
    SOCKET_LIST.append(client_socket)
    SOCKET_NICK_MAP.append((client_socket, username))
    # print(SOCKET_NICK_MAP)

def send(client_socket, message):
    try:
        client_socket.send(message + '\n')
        return True
    except:
        # disconnect and remove from SOCKET_LIST
        disconnect_socket(client_socket)
        return False

def send_pending_messages(client_socket, username):
    # get messages pending to <username> from database
    t = (username, )
    c.execute("SELECT * FROM messages WHERE dest=?", t)

    pending_messages = c.fetchall()
    c.execute("DELETE FROM messages WHERE dest=?", t)
    conn.commit()

    message_dict = {'messages' : []}
    
    for row in pending_messages:
        message_dict['messages'].append({
                    'source': row[1],
                    'dest': row[2],
                    'message': row[3]
                })

    m = json.dumps(message_dict)
    
    print(m)
    send(client_socket, m)


def log_out(server_socket, client_socket, addr):
    # tell everyone that user is going offline
    broadcast(server_socket, client_socket, "\r" + "[offline] " + get_username(client_socket) + " is offline\n") 

    # disconnect the socket and remove it from SOCKET_LIST
    disconnect_socket(client_socket)

def log_in(server_socket, client_socket, username):
    """
    To be called when a user is logged in / registered
    client_socket : socket to which the user is attached
    """
    # send user a ok message
    send(client_socket, '1')
    
    # recieve confirmation from user
    client_socket.recv(RECV_BUFFER)
    
    # send the list of users who are currently online
    send(client_socket, str([x[1] for x in SOCKET_NICK_MAP]))

    # add user to the SOCKET_LIST and SOCKET_NICK_MAP
    add_socket(client_socket, username)

    # send pending messages
    send_pending_messages(client_socket, username)

    # tell everyone that a new user has joined the room
    broadcast(server_socket, client_socket, "\r" + "[join] " + get_username(client_socket) + " has joined the room\n") 


def get_user_data(client_socket):

    # get data from client
    user_pass = client_socket.recv(RECV_BUFFER).rstrip()

    # message recieved from client is of the form "<username>,<password>" so split it
    user_pass = user_pass.split(',')

    # print(user_pass)
    return [user_pass[0], user_pass[1]]

def client_thread(server_socket, client_socket, addr):
    """
    must be invoked in a new thread
    """

    # start a loop in a new thread
    # loop is broken only if the client logs in or registers successfully    
    while True:
        # recieve command from client -- cmd will be one of ['\login', '\register']
        cmd = client_socket.recv(RECV_BUFFER).rstrip()

        if cmd == '\\register':
            print('New user registering : ', addr)

            # recieve username and password from client
            username, password = get_user_data(client_socket)

            # check if the username is already in use or not
            if not check_username(username):

                # add user to the database
                new_user(username, password)

                # log the user in
                log_in(server_socket, client_socket, username)

                break
            else:
                # username already exists in database
                send(client_socket, 'Nick already taken!')

        elif cmd == '\\login':
            print('user loggin in : ', addr)

            # recieve username and password from client
            username, password = get_user_data(client_socket)

            # check if the user is already logged in
            if is_already_logged_in(username):
                send(client_socket, 'user already logged in')
                print('user already logged in')

            # check the validity of credentials
            elif check_credentials(username, password):
                print(client_socket.getpeername(), ' joined!')
                
                # log the user in
                log_in(server_socket, client_socket, username)

                break
            else:
                # credentials are invalid
                send(client_socket, 'invalid username/pass')
                print('invalid username/pass')

        elif cmd == '\\ldaplogin':
            print('ldap user logging in : ', addr)

            # recieve username and password from client
            username, password = get_user_data(client_socket)

            # check if the user is already logged in
            if is_already_logged_in(username):
                send(client_socket, 'user already logged in')
                print('user already logged in') 
            else:
                # try ldap login
                user_dn = "cn=" + username + "," + base_dn

                try:
                    ldap_conn.protocol_version = ldap.VERSION3
                    print(ldap_conn.simple_bind_s(user_dn, password))
                    # log the user in
                    log_in(server_socket, client_socket, username)

                except ldap.INVALID_CREDENTIALS:
                    send(client_socket, 'invalid username/password')
                    print "Your username or password is incorrect."

                except ldap.LDAPError, e:
                    send(client_socket, 'error logging in')
                    if type(e.message) == dict and e.message.has_key('desc'):
                        print e.message['desc']
                    else: 
                        print e
        
        else:
            # command is invalid
            send(client_socket, 'Invalid command! try again')

def chat_server():
    """
    main server function
    runs in an infinite loop and keeps checking readability of connected sockets
    """

    # define server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # set options 
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # bind server socket to given HOST and PORT
    server_socket.bind((HOST, PORT))

    # listen for connections (upto 10)
    server_socket.listen(10)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    print("Server started at " + HOST + " on port " + str(PORT))
 
    while True:

        # get the list sockets which are ready to be read
        ready_to_read, _, _ = select.select(SOCKET_LIST,[],[],0)

        for sock in ready_to_read:

            # a new connection request recieved
            if sock == server_socket: 
                # accept the connection
                sockfd, addr = server_socket.accept()
                print('connected')

                # start client_thread() in a new thread
                thread.start_new_thread(client_thread, (server_socket, sockfd, addr))
         
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receive data from the socket.
                    data = sock.recv(RECV_BUFFER)

                    # username linked to sock
                    username = get_username(sock)

                    # DEBUG 
                    # show_database()

                    # if recieved data is not empty
                    if data:

                        data = data.rstrip()
                        message = data
                        to_user = 'broadcast'

                        # if data is of the form <username>@<message> then send it to that user
                        m = data.split('@')

                        if len(m) > 1:
                            to_user = m[0]
                            message = m[1]

                        # user wants to logout
                        if data == '\\logout':
                            log_out(server_socket, sock, addr)

                        elif to_user != 'broadcast':
                            # message to a specific user
                            # check if to_user is online
                            if to_user in [x[1] for x in SOCKET_NICK_MAP]:
                                send(get_socket(to_user), "\r" + 'message ' + username + ' ' + message)
                            else:
                                save_message(username, to_user, message)
                        else:
                            # send it to all connected users
                            broadcast(server_socket, sock, "\r" + 'broadcast ' + username + ' ' + message)  
                    else:
                        # empty data --> broken connection --> logout
                        log_out(server_socket, sock, addr)

                except:
                    # broken connection
                    log_out(server_socket, sock, addr)
                    continue

    # close the server
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


         