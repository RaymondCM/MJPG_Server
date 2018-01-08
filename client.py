#!/usr/bin/env python
import argparse
from threading import Thread
import cv2
import numpy as np
from six.moves.urllib import request


class MJPGDecoderThread(Thread):
    def __init__(self, url='http://127.0.0.1:8080/cam.mjpg'):
        Thread.__init__(self)
        self.url = url
        self.byte_chunks = 2048
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
            self.bytes += self.stream.read(self.byte_chunks)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", default="0.0.0.0", help="Server IP Address [Default 127.0.0.1]", dest="ip", type=str)
    parser.add_argument("-p", default=8080, help="Server Port [Default: 8080]", dest="port", type=int)
    parser.add_argument("-w", default=False, help="Wait for frame [Default: False]", dest="wait", type=bool)
    results = parser.parse_args()

    ip = results.ip
    port = results.port
    mjpg_url = 'http://{}:{}/cam.mjpg'.format(ip, port)
    wait_for_frame = results.wait  # Set to true to only preview new frames

    window_name = "Client Preview"
    cv2.namedWindow(window_name)

    try:
        decoder_thread = MJPGDecoderThread(mjpg_url)
        decoder_thread.setName("MJPEG Decoder Thread")
        decoder_thread.start()

        print("Press q in the rendering window to exit")

        while True:
            if decoder_thread.new_frame:
                cv2.imshow(window_name, decoder_thread.frame if wait_for_frame else decoder_thread.get_frame())
            key = cv2.waitKey(1)
            if key == ord('q') or key == ord('Q'):
                break
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        cv2.destroyWindow(window_name)
        decoder_thread.join_request = True
        decoder_thread.join()


if __name__ == '__main__':
    client()
