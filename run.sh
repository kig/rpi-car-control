#!/bin/bash

trap "echo Exiting...; pkill -P $$; exit 0" SIGINT SIGTERM SIGHUP

. /etc/rpi-car-control/env.sh

sudo mkdir -p /var/run/car
sudo chown pi /var/run/car

cd $(dirname "$0")

# Power off the Ethernet chipset and the USB ports next to it.
if lsusb -t | grep -q hub/3p
then
	echo "Shutting down eth USB"
	bin/eth_usb_down.sh
fi

if [ ! -z "$RPROXY_SERVER" ]
then
    echo "Starting SSH rproxy tunnel"
    (
        trap "echo Exiting Tunnel...; pkill -P $$; exit 0" SIGINT SIGTERM SIGHUP
        while true
        do
        ssh -o "StrictHostKeyChecking no" -o "ConnectTimeout 3" -o "ExitOnForwardFailure yes" -o "ServerAliveInterval 1" -o "ServerAliveCountMax 1" -i /home/pi/.ssh/id_rsa -R 9999:localhost:80 -N car@${RPROXY_SERVER} 2>/dev/null
            sleep 1
        done
    ) &
fi

echo "Starting web server"

cd web_server
python3.6 web.py
