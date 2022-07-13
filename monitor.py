import config
import datetime
import logging
import logging.handlers
import os
import pylogix
import time

from fault_video.camera import Camera


class Monitor(object):

    def __init__(self):
        self.cameras = []
        self.comm = None
        self.read = True

        self.handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "output/logjammin.log"))
        self.formatter = logging.Formatter(fmt="%(asctime)s  %(levelname)s: %(message)s")
        self.handler.setFormatter(self.formatter)
        self.root = logging.getLogger()
        self.root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
        self.root.addHandler(self.handler)

        self.setup()
        self.run()

    def setup(self):
        """
        Setup for monitoring
        """
        # create a camera thread for each camera that was
        # defined in the config
        for k,v in config.cameras.items():
            logging.info("Adding camera {} - {}".format(v, k))
            cam = Camera(self)
            cam.camera = v
            cam.cam_id = k
            cam.start()
            self.cameras.append(cam)

        # create output directory if it does not exist
        try:
            self.create_directories()
        except:
            logging.error("Failed to setup directories")
            self.read = False

    def run(self):
        """
        Loop, monitoring for faults
        """
        with pylogix.PLC(config.plc_ip, config.plc_slot) as self.comm:
            print("\nPress CTRL+C to exit")
            logging.info("Starting monitor, pylogix v{}".format(pylogix.__version__))

            while self.read:
                try:
                    # read the tag
                    ret = self.comm.Read(config.fault_tag)
                    time.sleep(1)
                    if ret.Value:
                        # if it's true, save the fault
                        self.fault_occured()

                        # write the fault tag back to 0
                        if config.acknowledge:
                            self.comm.Write(config.fault_tag, False)

                        while ret.Value:
                            # wait here until it is false 
                            ret = self.comm.Read(config.fault_tag)
                            time.sleep(1)
                except KeyboardInterrupt:
                    logging.warning("Keyboard interrupt")
                    self.close_cameras()
                    self.read = False
                except Exception as e:
                    logging.error("Monitor crashed... {}".format(e))
                    self.close_cameras()
                    self.read = False

    def close_cameras(self):
        """
        Close all cameras
        """
        logging.info("Closing cameras")
        for camera in self.cameras:
            # stop all cameras on exit
            camera.stop()
        return

    def create_directories(self):
        """
        Create an output directory and camera directories
        if they do not already exist
        """
        if not os.path.isdir("output"):
            logging.info("Output directory did not exist, creating now")
            os.mkdir("output")

        for camera in self.cameras:
            if not os.path.isdir("output/{}".format(camera.cam_id)):
                logging.info("Creating directory for camera id {}".format(camera.cam_id))
                os.mkdir("output/{}".format(camera.cam_id))

        return

    def fault_occured(self):
        """
        Fault occured, trigger a video save
        """
        logging.info("New fault occured, saving video buffers")
        for camera in self.cameras:
            camera.save()

        self.get_newest_videos()
        return

    def get_files(self, path, ext='', sort=False):
        """
        gets all files in a path. Files can be
        filtered and sorted.
        """
        files = []
        for f in os.listdir(path):
            if f.endswith(ext):
                files.append(f)
        if sort:
            return sorted(files, reverse=True)
        else:
            return files

    def get_newest_videos(self):
        """
        Get the newest video files for each camera
        """
        vids = []
        for camera in self.cameras:
            path = "output/{}/".format(camera.cam_id)
            files = self.get_files(path, ext=".mp4", sort=True)
            if files:
                s = "{}{}".format(path, files[0])
                vids.append(os.path.normpath(s))

        self.purge_old_videos()
        return

    def purge_old_videos(self):
        """
        Clear out older videos.  Max number of videos is defined
        in the config file
        """
        paths = ["output/{}/".format(camera.cam_id) for camera in self.cameras]
        for p in paths:
            p = os.path.abspath(p)
            if os.path.isdir(p):
                files = os.listdir(p)
                files.sort(reverse=True)
                excess = files[config.max_files:]
                if excess:
                    logging.info("Max videos exceeded, purging {}".format(e))
                    for e in excess:
                        logging.info("Max videos exceeded, purging {}".format(e))
                        os.remove("{}/{}".format(p, e))


if __name__ == "__main__":
    x = Monitor()
