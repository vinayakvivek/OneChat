# chat_client.py

import sys, socket, select

RECV_BUFFER = 4096
 
def chat_client():
    if(len(sys.argv) < 3) :
        print 'Usage : python chat_client.py hostname port'
        sys.exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print 'Unable to connect'
        sys.exit()
     
    print 'Connected to remote host. You can start sending messages'
    # sys.stdout.write('[Me] '); sys.stdout.flush()
    
    while True:
        cmd = raw_input('command : ')

        s.send(cmd)

        if cmd == '\\login':
            username = raw_input('username : ')
            s.send(username)

            password = raw_input('password : ')
            s.send(password)

            if s.recv(RECV_BUFFER).rstrip() == '1':
                print('logged in !')
                sys.stdout.write('[Me] '); sys.stdout.flush()  
                break
            else:
                print('Invalid username/password! pls try again')
        elif cmd == '\\register':
            username = raw_input('username : ')
            s.send(username)

            password = raw_input('password : ')
            s.send(password)

            status = s.recv(RECV_BUFFER).rstrip()
            if status == '1':
                print('registered successfully!')
                sys.stdout.write('[Me] '); sys.stdout.flush()  
                break
            else:
                print(status)
        else:
            msg = s.recv(RECV_BUFFER).rstrip()
            print(msg)
            
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list , [], [])
         
        for sock in read_sockets:            
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(4096)
                if not data :
                    print '\nDisconnected from chat server'
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(data)
                    sys.stdout.write('[Me] '); sys.stdout.flush()     
            
            else :
                # user entered a message
                msg = sys.stdin.readline()
                s.send(msg)
                sys.stdout.write('[Me] '); sys.stdout.flush() 

if __name__ == "__main__":

    sys.exit(chat_client())
