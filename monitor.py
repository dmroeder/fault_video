import config
import datetime
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
    while read:
        try:
            ret = comm.Read(config.fault_tag)
            time.sleep(1)
            if ret.Value:
                FaultHappend(cameras)
                while ret.Value:
                    ret = comm.Read(config.fault_tag)
                    time.sleep(1)
        except KeyboardInterrupt:
            for c in cameras:
                c.stop()
            print('exiting')
            read = False

