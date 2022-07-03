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
        self.buffer = []
        self.cap = None
        self.frame = None
        self.loop = False
        self.max_frames = config.frame_rate

    def run(self):
        """
        Capture frames and save them in a buffer of
        maximum size
        """
        print("Press CTRL+C to exit")
        self.cap = cv2.VideoCapture(self.camera)
        time.sleep(2)
        self.loop = True

        while self.loop:
            self.frame = self.cap.read()[1]

            if len(self.buffer) > self.max_frames:
                self.buffer = self.buffer[1:] + [self.frame]
            else:
                self.buffer += [self.frame]

    def save(self):
        """
        Save the buffer to a video
        """
        buffer = self.buffer
        now = datetime.datetime.now()
        date = now.strftime("%Y%m%d_%H.%M.%S")
        date = "output/{} - {}".format(self.cam_id, date)
        fn = "{}.mp4".format(date)
        writer = cv2.VideoWriter(fn, cv2.VideoWriter_fourcc(*"mp4v"), 20.0, config.resolution)
        for frame in buffer:
            writer.write(frame)
        writer.release()

    def stop(self):
        """
        Stop our thread, clean up
        """
        self.loop = False
        time.sleep(0.5)
        self.cap.release()
        cv2.destroyAllWindows()
