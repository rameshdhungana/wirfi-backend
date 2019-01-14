import socket
import selectors
import types

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

selector = selectors.DefaultSelector()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
print('Listening on ', HOST,':', PORT)
sock.setblocking(False)
selector.register(sock, selectors.EVENT_READ, data=None)


def accept_connection(sock):
    conn, addr = sock.accept()
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, received=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    selector.register(conn, events, data=data)

def serve_connection(key, mask):
    conn = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        data_received = conn.recv(1024)
        if data_received:
            with open(str(data.addr[0])+'_'+str(data.addr[1]),'w+') as filename:
                filename.write(str(data_received))

        else:
            selector.unregister(conn)
            conn.close()

    if mask & selectors.EVENT_WRITE:
        if data.received:
            print(data.received)

while True:
    events = selector.select()
    for key, mask in events:
        if key.data is None:
            accept_connection(key.fileobj)
        else:
            serve_connection(key, mask)

