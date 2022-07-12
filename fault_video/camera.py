import config
import cv2
import datetime
import threading
import time

class Camera(threading.Thread):

    def __init__(self):

        threading.Thread.__init__(self)
        
        self.cam_id = 0
        self.camera = 0
        
        self._buffer = []
        self._cap = None
        self._frame = None
        self._loop = False
        self._max_frames = int(config.video_length * 30)

    def run(self):
        """
        Capture frames and save them in a buffer of
        maximum size
        """
        self._cap = cv2.VideoCapture(self.camera)
        time.sleep(2)
        self._loop = True

        while self._loop:
            self._frame = self._cap.read()[1]

            if len(self._buffer) > self._max_frames:
                self._buffer = self._buffer[1:] + [self._frame]
            else:
                self._buffer += [self._frame]

    def save(self):
        """
        Save the buffer to a video
        """
        buffer = self._buffer
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d_%H.%M.%S")
        date = "output/{}/{}".format(self.cam_id, date)
        fn = "{}.mp4".format(date)
        writer = cv2.VideoWriter(fn, cv2.VideoWriter_fourcc(*"mp4v"), 30.0, config.resolution)
        for frame in buffer:
            writer.write(frame)
        writer.release()

    def stop(self):
        """
        Stop our thread, clean up
        """
        self._loop = False
        time.sleep(0.5)
        self._cap.release()
        cv2.destroyAllWindows()
