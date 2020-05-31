#!/bin/bash

sudo mkdir -p /var/run/car
sudo chown pi /var/run/car

if [ -e /var/run/car/controls.pid ]
then
    echo "Server already running at PID" `cat /var/run/car/controls.pid`
    echo "If this is not so, rm /var/run/car/controls.pid"
    echo "Exiting start_servers..."
    exit 1
fi

trap "echo Received signal. Exiting start_control_server PID $$; rm /var/run/car/controls.pid; pkill -P $$; exit 0" INT TERM HUP

echo "Starting servers"

echo $$ > /var/run/car/controls.pid

cd $(dirname "$0")

cd ..

echo "Starting car control server"
cd control/
  python3.6 car_websockets.py >/dev/null 2>&1 &
cd ..

echo "Servers running"

wait

echo "Server processes died for unknown reason"

rm /var/run/car/controls.pid
