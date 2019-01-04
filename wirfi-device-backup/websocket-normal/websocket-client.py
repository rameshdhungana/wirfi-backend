#!/usr/bin/env python

# WS client example

import asyncio
import websockets


async def hello():
    async with websockets.connect(
            'ws://localhost:9000') as websocket:
        name = input("What's your name? ")

        await websocket.send(name)
        print(f"> {name}")

        greeting = await websocket.recv()
        print(f"< {greeting}")

        # import cv2
        # import numpy as np
        # import socket
        # import sys
        # import pickle
        # import struct  ### new code
        # cap = cv2.VideoCapture(0)
        # clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # clientsocket.connect(('localhost', 8081))
        # while True:
        #     ret, frame = cap.read()
        #     data = pickle.dumps(frame)  ### new code
        #     clientsocket.sendall(struct.pack("H", len(data)) + data)


asyncio.get_event_loop().run_until_complete(hello())
