import config
import cv2
import datetime
import threading
import time

class Camera(threading.Thread):

    def __init__(self, parent):

        threading.Thread.__init__(self)
        self.daemon = True
        
        self.cam_id = 0
        self.camera = 0
        self.parent = parent
        
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

        if not self._cap.isOpened():
            self.parent.log("error", "Failed to open camera {}".format(self.camera))
            self._loop = False
        else:
            self.parent.log("info", "Camera {} started".format(self.camera))
            width = self._cap.get(3)
            height = self._cap.get(4)
            self.parent.log("info", "Frame dimensions: {}x{}".format(width, height))

        while self._loop:
            if self.parent.read == False:
                self.stop()
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
        fn = "output/{}/{}.mp4".format(self.cam_id, date)
        writer = cv2.VideoWriter(fn, cv2.VideoWriter_fourcc(*"mp4v"), 30.0, config.resolution)
        self.parent.log("info", "Saving file {}".format(fn))
        for frame in buffer:
            writer.write(frame)
        writer.release()

    def stop(self):
        """
        Stop our thread, clean up
        """
        self._loop = False
        time.sleep(0.5)
        try:
            self._cap.release()
        except:
            pass
        cv2.destroyAllWindows()
