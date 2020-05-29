#!/bin/bash

trap "echo Received signal. Exiting start_stream PID $$; rm /var/run/car/server.pid; pkill -P $$; exit 0" INT TERM HUP

raspivid -vf -hf -vs -ex auto -drc high -fli 50hz -mm matrix -ISO 0 -t 0 -n -o - -w 640 -h 480 -fps 60 -b 12500000 -cd MJPEG | raspivid_mjpeg_server

wait
exit

