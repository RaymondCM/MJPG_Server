import io
import threading
from datetime import datetime
from time import sleep
from util import is_linux
if is_linux():
    import picamera
else:
    import cv2


class Camera(object):
    thread = None
    frame = None
    last_access = 0
    pi_support = False
    width = 320
    height = 240
    size = height * width

    def initialize(self):
        Camera.pi_support = is_linux()

        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.stop_event = threading.Event()
            Camera.thread.start()

            # Return control to calling class when frame becomes available
            while self.frame is None:
                sleep(0)

    def get_frame(self):
        Camera.last_access = datetime.now()
        self.initialize()
        return self.frame

    @staticmethod
    def schedule_stop():
        Camera.thread.stop_event.set()

    @staticmethod
    def should_stop(timeout=10):
        return Camera.thread.stop_event.is_set() or (datetime.now() - Camera.last_access).total_seconds() > timeout

    @classmethod
    def _thread(cls):
        if cls.pi_support:
            with picamera.PiCamera() as camera:
                # camera setup
                camera.resolution = (cls.width, cls.height)
                camera.hflip = True
                camera.vflip = True

                # let camera warm up
                camera.start_preview()
                sleep(2)

                stream = io.BytesIO()
                for _ in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                    stream.seek(0)
                    cls.frame = stream.read()
                    stream.seek(0)
                    stream.truncate()

                    if cls.should_stop():
                        break
        else:
            capture = cv2.VideoCapture(0)
            success, frame = capture.read()
            cls.height, cls.width = frame.shape[:2]
            cls.size = cls.height * cls.width

            while success:
                success, frame = capture.read()
                cls.frame = cv2.imencode('.jpg', frame)[1].tobytes()

                if cls.should_stop():
                    break

        cls.thread = None
