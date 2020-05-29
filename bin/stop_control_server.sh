#!/bin/bash

if [ ! -e /var/run/car/controls.pid ]
then
    echo "Control server not running"
    exit 1
fi

PID=`cat /var/run/car/controls.pid`

echo "Sending SIGTERM to controls at PID" $PID
kill $PID

