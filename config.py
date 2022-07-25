# PLC IP address
plc_ip = "192.168.1.10"

# which slot the processor is in
plc_slot = 0

# BOOL tag that is 1 when a fault is present
fault_tag = "fault_detected"

# rate to check for fault condition
poll_rate = 1.0

# specify the desired video length (seconds).
# this will determine the number of frames to be
# kept in each camera buffer.  A 10 second clip
# will capture 300 frames (10s * 30fps)
video_length = 15

# camera dictionary.  ID:path
# the path can be an integer for local webcams or
# a web address for IP cameras
# cameras = {0: 0,
#            1: 1}

# example of also mapping a local webcam and an
# IP camera.  Every camera model has unique paths,
# check the manual for the camera for the path
cameras = {0: 1,
           1: "rtsp://192.168.1.91/streaming/channels/1"}

# define the image resolution
resolution = (640, 480)

# acknowledge flag.  If true, we'll write your fault_tag
# back to 0 after fault is recorded
acknowledge = True

# maximum number videos to keep for each camera.
# the oldest files will be purged
max_files = 50

# number of log files to keep
log_count = 3