#!/usr/bin/env python

import datetime
from time import sleep

import cv2
import numpy as np
from six.moves.urllib import request


class MJPGDecoder:
    def __init__(self, url='http://127.0.0.1:8080/cam.mjpg'):
        self.url = url
        self.bytes = bytes()
        self.stream = request.urlopen(self.url)

    def get_frame(self):
        while True:
            self.bytes += self.stream.read(1024)
            start = self.bytes.find(b'\xff\xd8')
            end = self.bytes.find(b'\xff\xd9')
            if start != -1 and end != -1:
                jpg = self.bytes[start:end + 2]
                self.bytes = self.bytes[end + 2:]
                return cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)


def client():
    try:
        while True:
            hz = 1.0 / 50.0
            decoder = MJPGDecoder('http://192.168.0.155:8080/cam.mjpg')
            start = datetime.datetime.now()
            frame = decoder.get_frame()
            elapsed = (datetime.datetime.now() - start).total_seconds()
            cv2.imshow("Client Preview", frame)
            if cv2.waitKey(int(hz - elapsed) if elapsed < hz else 1) == ord('q'):
                break
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == '__main__':
    client()
