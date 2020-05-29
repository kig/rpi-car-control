#!/bin/bash

sudo mkdir -p /var/run/car
sudo chown pi /var/run/car

if [ -e /var/run/car/server.pid ]
then
    echo "Server already running at PID" `cat /var/run/car/server.pid`
    echo "If this is not so, rm /var/run/car/server.pid"
    echo "Exiting start_servers..."
    exit 1
fi

trap "echo Received signal. Exiting start_servers PID $$; rm /var/run/car/server.pid; pkill -P $$; exit 0" INT TERM HUP

echo "Starting servers"

echo $$ > /var/run/car/server.pid

cd $(dirname "$0")

cd ..

#echo "Starting streaming server"
cd video/
  ./start_stream.sh &
#  echo "Starting audio receive server"
#  python3.6 receive_audio.py >/dev/null 2>&1 &
cd ..

echo "Servers running"

wait

echo "Server processes died for unknown reason"

rm /var/run/car/server.pid
