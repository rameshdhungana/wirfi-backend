import socket
import sys
import numpy
with open('video.mp4','r',encoding='utf-8') as file:
    data = file.read()

    frame = numpy.fromstring(data, dtype=numpy.uint8)
    frame = numpy.reshape(frame, (240,320,3))