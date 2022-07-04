# fault_video
An example of capturing a video using a ring buffer

This is a basic demonstration of saving camera frames in a ring buffer, then saving
them to a video clip when a machine fault happens.  The result will be a video clip
leading up to when a fault condition is detected.  OpenCV is used to capture the video
frames, pylogix is used for monitoring a tag for a fault condition.  Webcams and IP cameras
are supported.

The camera defination in the config is a dict, where the key is the camera ID (just used in
the file name) and the path to the camera.  Local cameras (built in web cams or USB cameras)
will be an integer.  In my case, I have a built in webcam and a USB camera, they are index
0 and 1 respectively.  My particular model of IP camera is at the path:
rtsp://ip_address/streaming/channels/1.  See your manufactures documentation for your specific
cameras path.

The result will be mp4's saved in the output directory, name will be camera number defined in
the camera config and the time stamp.  For example: "0 - 20220703_09.31.58.mp4"