import config
import datetime
import os
import pylogix
import time

from fault_video.camera import Camera

def fault_occured(c):
    # this should get called once.
    for camera in c:
        camera.save()

def create_directories(cams):
    """
    Create an output directory and camera directories
    if they do not already exist
    """
    if not os.path.isdir("output"):
        os.mkdir("output")

    for c in cams:
        if not os.path.isdir("output/{}".format(c.cam_id)):
            os.mkdir("output/{}".format(c.cam_id))


with pylogix.PLC(config.plc_ip, config.plc_slot) as comm:
    cameras = []

    # create a camera thread for each camera that was
    # defined in the config
    for k,v in config.cameras.items():
        cam = Camera()
        cam.camera = v
        cam.cam_id = k
        cam.start()
        cameras.append(cam)

    # create output directory if it does not exist
    create_directories(cameras)

    print("\nPress CTRL+C to exit")
    read = True
    while read:
        try:
            # read the tag
            ret = comm.Read(config.fault_tag)
            time.sleep(1)
            if ret.Value:
                # if it's true, save the fault
                fault_occured(cameras)

                # write the fault tag back to 0
                if config.acknowledge:
                    comm.Write(config.fault_tag, False)

                while ret.Value:
                    # wait here until it is false 
                    ret = comm.Read(config.fault_tag)
                    time.sleep(1)
        except KeyboardInterrupt:
            for c in cameras:
                # stop all cameras on exit
                c.stop()
            read = False

