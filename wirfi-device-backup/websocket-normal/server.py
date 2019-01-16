import cv2
import zmq
import base64
import numpy as np
from datetime import datetime
import boto3
from django.http.response import StreamingHttpResponse

client = boto3.client('s3')

video_length = 0.001
context = zmq.Context()
footage_socket = context.socket(zmq.SUB)
footage_socket.bind('tcp://*:5555')
footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

# fourcc =cv2.VideoWriter_fourcc(*'MP4V')
fourcc = cv2.VideoWriter_fourcc(*"mp4v")

# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
# video = cv2.VideoWriter('video%d.avi'%count, fourcc, 20.0, (640,480))

last = datetime.now()

device_serial_number_list = []


def increase_counter(device_serial_number):
    global last, video

    now = datetime.now()
    if (now - last).seconds >= video_length:
        last = now
        # In every interval of set video_length, new file will be used to capture the video and save, file name is made
        # dynamic with datetime
        video_writer_objects[device_serial_number] = cv2.VideoWriter(
            '/home/insightworkshop/IwProjects/Projects/wirfi-web/media/webcam-videos/video_%s_%s.mp4' % (
                device_serial_number, last.strftime("%Y_%m_%d_%H_%M_%S")),
            fourcc, 20.0, (640, 480))


video_writer_objects = {}


def create_video_writer_object(device_serial_number):
    global video_writer_list
    video_writer_objects[device_serial_number] = cv2.VideoWriter(
        '/home/insightworkshop/IwProjects/Projects/wirfi-web/media/webcam-videos/video_%s_%s.mp4' % (
            device_serial_number, last.strftime("%Y_%m_%d_%H_%M_%S")),
        fourcc, 20.0, (640, 480))


while True:
    try:
        received_data = footage_socket.recv_json()
        # print(received_data)
        device_serial_number = received_data['device_serial_number']
        if not device_serial_number in device_serial_number_list:
            device_serial_number_list.append(device_serial_number)
            create_video_writer_object(device_serial_number)

        frame = received_data['camera_data']
        print(device_serial_number)
        # print(frame)

        img = base64.b64decode(frame)
        npimg = np.fromstring(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        video_writer_objects[device_serial_number].write(source)

        # function is called everytime but the params changes on video_length variable value interval
        increase_counter(device_serial_number)
        video_length = 20

        streaming_url = StreamingHttpResponse(source, content_type='multipart/x-mixed-replace;boundary=frame')
        print(streaming_url)
        # cv2.imshow("Stream", source)
        cv2.waitKey(1)


    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        break
