#!/usr/bin/env python

import datetime
from time import sleep

import cv2
import numpy as np
from six.moves.urllib import request
from threading import Thread


class MJPGDecoderThread(Thread):
    def __init__(self, url='http://127.0.0.1:8080/cam.mjpg'):
        Thread.__init__(self)
        self.url = url
        self.bytes = bytes()
        self.stream = request.urlopen(self.url)
        self.frame = np.array((1, 1, 3), dtype=np.uint8)
        self.new_frame = False
        self.join_request = False

    def get_frame(self):
        self.new_frame = False
        return self.frame

    def run(self):
        while True:
            self.bytes += self.stream.read(1024)
            start = self.bytes.find(b'\xff\xd8')
            end = self.bytes.find(b'\xff\xd9')

            if start != -1 and end != -1:
                jpg = self.bytes[start:end + 2]
                self.bytes = self.bytes[end + 2:]
                self.frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                self.new_frame = True

            if self.join_request:
                break


def client():
    window_name = "Client Preview"
    cv2.namedWindow(window_name)

    mjpg_url = 'http://192.168.0.155:8080/cam.mjpg'
    wait_for_frame = False  # Set to true to only preview new frames

    try:
        decoder_thread = MJPGDecoderThread(mjpg_url)
        decoder_thread.setName("MJPEG Decoder Thread")
        decoder_thread.start()

        while True:
            if decoder_thread.new_frame:
                cv2.imshow(window_name, decoder_thread.frame if wait_for_frame else decoder_thread.get_frame())
            if cv2.waitKey(1) == ord('q'):
                break
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        cv2.destroyWindow(window_name)
        decoder_thread.join_request = True
        decoder_thread.join()

if __name__ == '__main__':
    client()
