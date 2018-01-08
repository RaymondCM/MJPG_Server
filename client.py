#!/usr/bin/env python
import argparse
from threading import Thread
import cv2
import numpy as np
from six.moves.urllib import request
from util import unique_str

ros_imported = True
try:
    import rospy
    from sensor_msgs.msg import Image
    from cv_bridge import CvBridge, CvBridgeError
except ImportError:
    ros_imported = False


class MJPGDecoderThread(Thread):
    def __init__(self, url='http://127.0.0.1:8080/cam.mjpg', size=2048):
        Thread.__init__(self)
        self.url = url
        self.byte_chunks = size
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


class MJPGNode:
    def __init__(self, name, decoder, wait=False):
        self.image_pub = rospy.Publisher(name, Image)
        self.decoder_thread = decoder
        self.wait_for_frame = wait
        self.bridge = CvBridge()

    def start(self):
        while not rospy.is_shutdown():
            if self.decoder_thread.new_frame:
                frame = self.decoder_thread.frame if self.wait_for_frame else self.decoder_thread.get_frame()

                try:
                    message = self.bridge.cv2_to_imgmsg(frame, "bgr8")
                    message.header.stamp = rospy.Time.now()
                    self.image_pub.publish(self.bridge.cv2_to_imgmsg(frame, "bgr8"))
                except CvBridgeError as e:
                    print(e)


def client():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", default="0.0.0.0", help="Server IP Address [Default 127.0.0.1]", dest="ip", type=str)
    parser.add_argument("-p", default=8080, help="Server Port [Default: 8080]", dest="port", type=int)
    parser.add_argument("-w", default=False, help="Wait for frame [Default: False]", dest="wait", type=bool)
    parser.add_argument("-c", default=2048, help="Byte chunk size [Default: 2048]", dest="bsize", type=int)
    parser.add_argument("-n", default="auto", help="Node name [Default: auto]", dest="name", type=str)
    parser.add_argument("-r", default=False, help="Publish on ros node [Default: False]", dest="ros_sup", type=bool)
    results = parser.parse_args()

    ip = results.ip
    port = results.port
    mjpg_url = 'http://{}:{}/cam.mjpg'.format(ip, port)
    wait_for_frame = results.wait  # Set to true to only preview new frames
    chunk_size = results.bsize
    ros_support = results.ros_sup
    name = unique_str(name="camera") if results.name == "auto" else results.name

    if ros_support and not ros_imported:
        print("Couldn't enable ros support due to missing python libraries (rospy, sensor.msgs, cvbridge)")
        ros_support = False

    decoder_thread = MJPGDecoderThread(url=mjpg_url, size=chunk_size)
    decoder_thread.setName("MJPEG Decoder Thread {}".format(name))
    decoder_thread.start()

    try:
        if ros_support:
            print("Initialising anonymous ros node {}".format(name))
            rospy.init_node(name, anonymous=True)
            mjpg_node = MJPGNode(name, decoder_thread, wait_for_frame)
            mjpg_node.start()
            rospy.spin()
        else:
            print("Press q in the rendering window to exit")
            window_name = "Client Preview"
            cv2.namedWindow(window_name)

            while True:
                if decoder_thread.new_frame:
                    cv2.imshow(window_name, decoder_thread.frame if wait_for_frame else decoder_thread.get_frame())

                key = cv2.waitKey(1)
                if key == ord('q') or key == ord('Q'):
                    break
    except KeyboardInterrupt:
        print("Shutting down")
    finally:
        cv2.destroyAllWindows()
        decoder_thread.join_request = True
        decoder_thread.join()


if __name__ == '__main__':
    client()
