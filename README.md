# fault_video
An example of capturing a video using a ring buffer

This is a basic demonstration of saving camera frames in a ring buffer, then saving
them to a video clip when a machine fault happens.  The result will be a video clip
leading up to when a fault condition is detected.  OpenCV is used to capture the video
frames, pylogix is used for monitoring a tag for a fault condition.  Webcams and IP cameras
are supported.

The camera definition in the config is a dict, where the key is the camera ID (just used in
the file name) and the path to the camera.  Local cameras (built in web cams or USB cameras)
will be an integer.  In my case, I have a built in webcam and a USB camera, they are index
0 and 1 respectively.  My particular model of IP camera is at the path:
rtsp://ip_address/streaming/channels/1.  See your manufactures documentation for your specific
cameras path.

When launched, an output directory will be created, in side of it, a directory for each camera
that was defined in the config file.  Video clips will be saved in the camera directories.
You can define in the config file the maximum number of video clips you want to keep, the oldest
will be purged with each new clip recorded.

CPU utilization is pretty low with this method since the buffer is saved in memory until the
request is made to save the video clip.  So the number of cameras, length of buffer and the
resolution desired will determine the amount of memory that will be used while running.  The
default config values will use something like ~600MB of RAM.  I have ran it on a
Raspberry Pi 4, it performed reasonably well.  

## Requirements
* python 3
* opencv-python
* pylogix

To run, make sure you setup your configuration file, then:
```console
pylogix@pylogix-kde:~$ python monitor.py
```

