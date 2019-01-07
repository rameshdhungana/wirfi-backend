import socket
import sys
import cv2
import pickle
import struct

# Create a TCP/IP socket
import numpy

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 9000)
print >> sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)


# while True:
    # print >> sys.stderr, '\nwaiting to receive message'
    # data, address = sock.recvfrom(65535)
    # # frame = numpy.fromstring(data, dtype=numpy.uint8)
    # # frame = numpy.reshape(frame, (300, 100, 3))
    #
    # print >> sys.stderr, 'received %s bytes from %s' % (len(data), address)
    # print >> sys.stderr, data
    #
    # if data:
    #     sent = sock.sendto(data, address)
    #     print >> sys.stderr, 'sent %s bytes back to %s' % (sent, address)


### new
data = ""
payload_size = struct.calcsize("L")
while True:
    while len(data) < payload_size:
        data += sock.recv(7500)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]
    while len(data) < msg_size:
        data += sock.recv(7500)
    frame_data = data[:msg_size]
    data = data[msg_size:]
    ###

    frame=pickle.loads(frame_data)
    print frame
    cv2.imshow('frame',frame)

