import io
import threading
from datetime import datetime
from time import sleep
from util import is_linux, raspberrypi, thermal
if is_linux():
    import picamera
else:
    import cv2


class Camera(object):
    thread = None
    frame = None
    last_access = datetime.now()
    device_type = ""
    width = 320
    height = 240
    size = height * width

    def initialize(self, device_type="auto"):
        if device_type == "auto":
            Camera.device_type = "pi" if is_linux() else "cv"

        if Camera.thread is None:
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.stop_event = threading.Event()
            Camera.thread.start()

            # Return control to calling class when frame becomes available
            while self.frame is None:
                sleep(0)

    def get_frame(self):
        Camera.last_access = datetime.now()
        return self.frame

    def schedule_stop(self):
        if self.thread is not None:
            self.thread.stop_event.set()

    @staticmethod
    def should_stop(timeout=10):
        return Camera.thread.stop_event.is_set() or (datetime.now() - Camera.last_access).total_seconds() > timeout

    @classmethod
    def _thread(cls):
        if cls.device_type == raspberrypi():
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
        elif cls.device_type == thermal():
            # Thermal camera code goes here
            pass
        else:  # Default to default system camera device
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
