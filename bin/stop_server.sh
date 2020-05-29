#!/bin/bash

if [ ! -e /var/run/car/server.pid ]
then
    echo "Server not running"
    exit 1
fi

PID=`cat /var/run/car/server.pid`

echo "Sending SIGTERM to server at PID" $PID
kill $PID
