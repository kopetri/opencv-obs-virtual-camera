import pyvirtualcam
from threading import Thread
import cv2
import datetime
import numpy as np

class VirtualCamera:
    def __init__(self, cam_id=0, fps=120, mirror_image=False):
        self.mirror_image = mirror_image
        self.camera = CameraThread(cam_id)
        self.measure = FPS()
        self.virtual_camera = pyvirtualcam.Camera(width=self.camera.width(), height=self.camera.height(), fps=fps)
        self.running = False
        print("Streaming with resolution: {}x{}".format(self.camera.width(), self.camera.height()))

    def run(self):
        try:
            self.__run__()
        except:
            pass
        finally:
            self.stop()

    def __run__(self):
        self.measure.start()
        self.camera.start()
        self.running = True
        while self.running:
            frame = self.camera.read()
            frame = cv2.putText(frame, self.measure.info(), (80,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (240,240,240), 2, cv2.LINE_AA)            
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            if self.mirror_image:
                frame = cv2.flip(frame, 1)
            self.virtual_camera.send(frame)
            self.virtual_camera.sleep_until_next_frame()
            
    def stop(self):
        self.running = False
        self.camera.stop()
        self.virtual_camera.close()


class CameraThread:
    def __init__(self, cam=0):
        self.stream = cv2.VideoCapture(cam)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        (_, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def stop(self):
        self.stopped = True
        
    def update(self):
        while True:
            if self.stopped:
                return
            (_, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def width(self):
        return self.frame.shape[1]

    def height(self):
        return self.frame.shape[0]

class FPS:
    def __init__(self):
        self._n = 100
        self._times = np.zeros(self._n)
        self._i = 0

    def start(self):
        self._start = datetime.datetime.now()

    def elapsed(self):
        self._i = self._i % self._n
        self._times[self._i] = (datetime.datetime.now() - self._start).total_seconds()
        self._start = datetime.datetime.now()
        self._i += 1
        return np.mean(self._times) + 0.0000001
        
    def fps(self):
        return 1.0 / self.elapsed()

    def info(self):
        return "{} fps".format(round(self.fps(), 2))


vcam = VirtualCamera(mirror_image=False)
vcam.run()