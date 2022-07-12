import config
import datetime
import os
import pylogix
import time

from fault_video.camera import Camera


class Monitor(object):

    def __init__(self):
        self.cameras = []
        self.comm = None
        self.read = True

        self.setup()
        self.run()

    def setup(self):
        """
        Setup for monitoring
        """
        # create a camera thread for each camera that was
        # defined in the config
        for k,v in config.cameras.items():
            cam = Camera(self)
            cam.camera = v
            cam.cam_id = k
            cam.start()
            self.cameras.append(cam)

        # create output directory if it does not exist
        try:
            self.create_directories()
        except:
            self.read = False

    def run(self):
        """
        Loop, monitoring for faults
        """
        with pylogix.PLC(config.plc_ip, config.plc_slot) as self.comm:
            print("\nPress CTRL+C to exit")

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
                    self.close_cameras()
                    self.read = False
                except:
                    self.close_cameras()
                    self.read = False

    def close_cameras(self):
        """
        Close all cameras
        """
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
            os.mkdir("output")

        for camera in self.cameras:
            if not os.path.isdir("output/{}".format(camera.cam_id)):
                os.mkdir("output/{}".format(camera.cam_id))

        return

    def fault_occured(self):
        """
        Fault occured, trigger a video save
        """
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

        vids = []
        for camera in self.cameras:
            path = "output/{}/".format(camera.cam_id)
            files = self.get_files(path, ext=".mp4", sort=True)
            if files:
                s = "{}{}".format(path, files[0])
                vids.append(os.path.normpath(s))

        return



if __name__ == "__main__":
    x = Monitor()
