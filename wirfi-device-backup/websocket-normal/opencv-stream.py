# import numpy as np
# import cv2, socket
#
# cap = cv2.VideoCapture(0)
# import sys

# while (True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#
#     # Our operations on the frame come here
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     device_socket.connect(('localhost', 9000))
#     frame = frame.flatten()
#     data = frame.tostring()
#     device_socket.send(frame)
#
#     # Display the resulting frame
#     cv2.imshow('frame', gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()


# !/usr/bin/env python

# WS client example

#
# async def hello():
#     async with websockets.connect(
#             'ws://localhost:9000') as websocket:
#
#         import cv2
#         import socket
#         while (True):
#             # Capture frame-by-frame
#             ret, frame = cap.read()
#
#             # Our operations on the frame come here
#             gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#             device_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#             device_socket.connect(('localhost', 9000))
#             frame = frame.flatten()
#             data = frame.tostring()
#             device_socket.send(frame)
#
#             # Display the resulting frame
#             cv2.imshow('frame', gray)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#
#
# asyncio.get_event_loop().run_until_complete(hello())

import socket
import sys
import cv2
import pickle
import struct

# Create a UDP socket
device_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 9000)
message = 'This is the message.  It will be repeated.'

try:

    # Send data
    print >> sys.stderr, 'sending "%s"' % message
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 300)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 100)
    cap.set(cv2.CAP_PROP_FPS, 60)
    print(cap.get(cv2.CAP_PROP_FPS))

    ret, frame = cap.read()

    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame = cv2.resize(frame, (50, 50))

        # Our operations on the frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # frame = frame.flatten()
        # data = frame.tostring()
        print(frame.size, 'frame size')

        data = pickle.dumps(frame)
        print(len(data), 'len size')

        device_socket.sendto(struct.pack("L", len(data)) + data, server_address)
        # print(data)
        # Display the resulting frame
        cv2.imshow('frame', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print >> sys.stderr, 'waiting to receive'
    data, server = device_socket.recvfrom(4096)
    print >> sys.stderr, 'received "%s"' % data

finally:
    print >> sys.stderr, 'closing socket'
    device_socket.close()

# following code is for writing video (mp4 format file )
# import numpy as np
# import cv2
#
# cap = cv2.VideoCapture(0)
#
# # Define the codec and create VideoWriter object
# fourcc =cv2.VideoWriter_fourcc(*'MP4V')
# #out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
# out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640,480))
#
# while(cap.isOpened()):
#     ret, frame = cap.read()
#     if ret==True:
#         frame = cv2.flip(frame,0)
#
#         # write the flipped frame
#         out.write(frame)
#
#         cv2.imshow('frame',frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     else:
#         break
#
# # Release everything if job is finished
# cap.release()
# out.release()
# cv2.destroyAllWindows()
