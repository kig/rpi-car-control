#!/bin/bash

trap "echo Received signal. Exiting start_stream PID $$; pkill -P $$; exit 0" INT TERM HUP

. /etc/rpi-car-control/env.sh

if [ $VIDEO_MODE == "v4l2-mjpeg" ]; then
    # USB webcam
    v4l2-ctl -d ${V4L2_DEVICE} --set-ctrl=rotate=${VIDEO_ROTATION}
    gst-launch-1.0 v4l2src device=${V4L2_DEVICE} ! image/jpeg,width=${VIDEO_WIDTH},height=${VIDEO_HEIGHT},framerate=${VIDEO_FPS}/1 ! filesink buffer-size=0 location=/dev/stdout | ../bin/raspivid_mjpeg_server &
elif [ $VIDEO_MODE == "v4l2-raw" ]; then
    # Camera with only raw output, encode to JPEG first (TODO: integrate https://github.com/hopkinskong/rpi-omx-jpeg-encode or gst-omx omxmjpegenc)
    VIDEO_DIRECTION="identity"
    if [ $VIDEO_ROTATION == "90" ]; then
        VIDEO_DIRECTION="90l"
    elif [ $VIDEO_ROTATION == "180" ]; then
        VIDEO_DIRECTION="180"
    elif [ $VIDEO_ROTATION == "270" ]; then
        VIDEO_DIRECTION="90r"
    fi
    gst-launch-1.0 v4l2src device=${V4L2_DEVICE} ! video/x-raw,width=${VIDEO_WIDTH},height=${VIDEO_HEIGHT},framerate=${VIDEO_FPS}/1 ! videoflip video-direction=${VIDEO_DIRECTION} ! jpegenc ! filesink buffer-size=0 location=/dev/stdout | ../bin/raspivid_mjpeg_server &
else
    # Raspivid
    raspivid -rot ${VIDEO_ROTATION} -vs -ex auto -drc high -fli 50hz -mm matrix -ISO 0 -t 0 -n -o - -w ${VIDEO_WIDTH} -h ${VIDEO_HEIGHT} -fps ${VIDEO_FPS} -b 12500000 -cd MJPEG | ../bin/raspivid_mjpeg_server &
fi

wait
exit
