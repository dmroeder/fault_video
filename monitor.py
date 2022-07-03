import config
import datetime
import os
import pylogix
import time

from fault_video.camera import Camera

def FaultHappend(c):
    # this should get called once.
    for camera in c:
        camera.save()

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
    
    read = True

    if not os.path.isdir('output'):
        os.mkdir("output")

    while read:
        try:
            # read the tag
            ret = comm.Read(config.fault_tag)
            time.sleep(1)
            if ret.Value:
                # if it's true, save the fault
                FaultHappend(cameras)
                while ret.Value:
                    # wait here until it is false 
                    ret = comm.Read(config.fault_tag)
                    time.sleep(1)
        except KeyboardInterrupt:
            for c in cameras:
                # stop all cameras on exit
                c.stop()
            read = False

