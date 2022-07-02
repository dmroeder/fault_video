# PLC IP address
plc_ip = "192.168.1.10"

# which slot the processor is in
plc_slot = 0

# BOOL tag that is 1 when a fault is present
fault_tag = "h_Global[5].Indicator"

# the number of frames to be stored in the buffer
frame_rate = 300

# camera dictionary.  ID:path
# the path can be an integer for local webcams or
# a web address for IP cameras
cameras = {0: 0}
