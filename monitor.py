"""
   Maintained by Dustin Roeder (dmroeder@gmail.com)

   Copyright 2022 Dustin Roeder

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import config
import datetime
import fault_video
import logging
import logging.handlers
import os
import pylogix
import sys
import time

from fault_video.camera import Camera


class Monitor(object):

    def __init__(self):
        self.cameras = []
        self.comm = None
        self.read = True

        self.handler = logging.handlers.RotatingFileHandler('output/logjammin.log', maxBytes=10000, backupCount=config.log_count)
        self.formatter = logging.Formatter(fmt="%(asctime)s  %(levelname)s: %(message)s")
        self.handler.setFormatter(self.formatter)
        self.root = logging.getLogger()
        self.root.setLevel(os.environ.get("LOGLEVEL", "DEBUG"))
        self.root.addHandler(self.handler)

        self.newest_videos = []

        self.setup()
        self.run()

    def setup(self):
        """
        Setup for monitoring
        """
        self.log("debug", "----------")
        self.log("debug", "v{}".format(fault_video.__version__))
        # log the configuration
        self.log("debug", "PLC IP/Slot - {}/{}".format(config.plc_ip, config.plc_slot))
        self.log("debug", "Micro800 - {}".format(config.micro800))
        self.log("debug", "PLC Tag - {}".format(config.fault_tag))
        self.log("debug", "Video Length - {}".format(config.video_length))
        self.log("debug", "Resolution - {}x{}".format(*config.resolution))
        self.log("debug", "Acknowledge flag - {}".format(config.acknowledge))
        self.log("debug", "Max files - {}".format(config.max_files))

        # create a camera thread for each camera that was
        # defined in the config
        for k,v in config.cameras.items():
            self.log("info", "Adding camera {} - {}".format(v, k))
            cam = Camera(self)
            cam.camera = v
            cam.cam_id = k
            cam.start()
            self.cameras.append(cam)

        # create output directory if it does not exist
        try:
            self.create_directories()
        except:
            self.log("error", "Failed to create directories")
            self.read = False
        return

    def run(self):
        """
        Loop, monitoring for faults
        """
        with pylogix.PLC(config.plc_ip, config.plc_slot, Micro800=config.micro800) as self.comm:
            self.log("info", "Starting PLC communications")
            print("\nPress CTRL+C to exit")

            ret = self.comm.Read(config.fault_tag)
            if ret.Status == "Success":
                self.log("info", "Successfully connected to the PLC")
            else:
                self.log("error", "Pylogix error: {}".format(ret.Status))
                self.read = False

            # read the tag, if it is true initially, hang here
            # until it is false.  We don't want to save a clip if
            # there is a fault on startup
            while ret.Value == True:
                time.sleep(config.poll_rate)
                # write the fault tag back to 0
                if config.acknowledge:
                    self.comm.Write(config.fault_tag, False)

                ret = self.comm.Read(config.fault_tag)

            while self.read:
                try:
                    # read the tag
                    ret = self.comm.Read(config.fault_tag)
                    time.sleep(config.poll_rate)
                    if ret.Value:
                        self.log("info", "Fault detected")
                        # if it's true, save the fault
                        self.fault_occured()

                        # write the fault tag back to 0
                        if config.acknowledge:
                            self.comm.Write(config.fault_tag, False)

                        while ret.Value:
                            # wait here until it is false 
                            ret = self.comm.Read(config.fault_tag)
                            time.sleep(config.poll_rate)
                except KeyboardInterrupt:
                    self.log("info", "Keyboard interrupt, shutting down")
                    self.read = False
                except Exception as e:
                    self.log("error", "Error occured: {}".format(e))
                    self.read = False

        # if our loop exited, try to close the cameras
        self.log("info", "Closing cameras")
        self.close_cameras()
        sys.exit(0)

    def log(self, level, message):
        """
        Log messages to our log file
        """
        if level == "info":
            logging.info(message)
        elif level == "error":
            logging.error(message)
        elif level == "debug":
            logging.debug(message)
        return

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
        if config.video_path_tags:
            self.send_path()
        return

    def send_path(self):
        """
        Write the latest video path to the PLC
        """
        for i, v in enumerate(self.newest_videos):
            try:
                tag = config.video_path_tags[i]
                ret = self.comm.Write(tag, v)
                if ret.Status != "Success":
                    self.log("error", "Failed to write to path tag {}, {}".format(tag, ret.Status))
            except:
                tags = ','.join(str(x) for x in config.video_path_tags)
                self.log("error", "Failed to write video paths to PLC - {}".format(tags))

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
        source = os.getcwd()
        for camera in self.cameras:
            path = "output/{}/".format(camera.cam_id)
            files = self.get_files(path, ext=".mp4", sort=True)
            if files:
                s = "{}\{}{}".format(source, path, files[0])
                vids.append(os.path.normpath(s))

        self.purge_old_videos()
        self.newest_videos = vids
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
                    for e in excess:
                        os.remove("{}/{}".format(p, e))


if __name__ == "__main__":
    x = Monitor()
