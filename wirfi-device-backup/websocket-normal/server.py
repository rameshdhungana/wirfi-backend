import cv2
import zmq
import base64
import numpy as np
from datetime import datetime

video_length = 30
context = zmq.Context()
footage_socket = context.socket(zmq.SUB)
footage_socket.bind('tcp://*:5555')
footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

# fourcc =cv2.VideoWriter_fourcc(*'MP4V')
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
# video = cv2.VideoWriter('video%d.avi'%count, fourcc, 20.0, (640,480))

last = datetime.now()
# declaration of video , it will be global
video = cv2.VideoWriter('video_%s.mp4' % last.strftime("%Y_%m_%d_%H:%M:%S"), fourcc, 20.0, (640, 480))


def increase_counter():
    global last, video

    now = datetime.now()
    if (now - last).seconds >= video_length:
        last = now
        # In every interval of set video_length, new file will be used to capture the video and save, file name is made
        # dynamic with datetime
        video = cv2.VideoWriter('video_%s.mp4' % last.strftime("%Y_%m_%d_%H:%M:%S"), fourcc, 20.0, (640, 480))

        print(last.strftime("%Y-%m-%d-%H:%M:%S"))


while True:
    try:
        frame = footage_socket.recv_string()
        print(frame)
        img = base64.b64decode(frame)
        npimg = np.fromstring(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        video.write(source)
        # function is called everytime but the params changes on video_length variable value
        increase_counter()
        # cv2.imshow("Stream", source)
        cv2.waitKey(1)


    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break

