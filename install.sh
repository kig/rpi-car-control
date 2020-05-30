#!/bin/bash

sudo apt update

sudo apt install -y nginx sox libsox-fmt-mp3 rws ffmpeg

sudo cp /etc/nginx/available-sites/default /etc/nginx/available-sites/default.bak
sudo cp etc/nginx.conf /etc/nginx/available-sites/default

sudo cp etc/car.service /etc/systemd/system/

sudo systemctl enable car.service


sudo apt install -y ansible

if [ ! -f ~/.ssh/id_rsa.pub ]
then
  ssh-keygen -q -N "" -f ~/.ssh/id_rsa
fi

if [ -f ~/.ssh/authorized_keys ]
then
  mv ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak
fi

cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

ssh -o "StrictHostKeyChecking no" localhost echo "Added localhost to .ssh/known_hosts" 2>/dev/null
ansible-playbook -i localhost, raspbian-python3.6.yml

if [ -f ~/.ssh/authorized_keys.bak ]
then
  mv ~/.ssh/authorized_keys.bak ~/.ssh/authorized_keys
else
  rm ~/.ssh/authorized_keys
fi

sudo pip3.6 install --upgrade pip setuptools wheel
sudo pip3.6 install rpi.gpio
sudo pip3.6 install websockets
sudo pip3.6 install smbus2
sudo pip3.6 install vl53l1x
sudo pip3.6 install Adafruit_DHT

(
  # Install Rust
  curl https://sh.rustup.rs -sSf | sh
  . ~/.cargo/env 

  # Clone the raspivid_mjpeg_server repo and build and install the server
  git clone https://github.com/kig/raspivid_mjpeg_server
  cd raspivid_mjpeg_server
  echo "Building raspivid_mjpeg_server. This is going to take forever (15 minutes on Raspberry Pi 3B+) so do some pushups in the meanwhile."
  cargo build --release
  cp target/release/raspivid_mjpeg_server ../bin/
)

sudo mkdir -p /opt/rpi-car-control
sudo cp -r bin control html sensors video web_server run.sh /opt/rpi-car-control

echo "The car is installed"
echo
echo "For rproxy SSH server:"
echo "----------------------"
echo 'export RPROXY=my.rproxy.server'
echo 'ssh $RPROXY -- "sudo useradd car -s /bin/false"; sudo mkdir ~car/.ssh; sudo touch ~car/.ssh/authorized_keys; sudo chmod -R go-rwx ~car/.ssh'
echo 'ssh $RPROXY -- "cat >> sudo tee ~car/.ssh/authorized_keys" < ~/.ssh/id_rsa.pub'
echo 'ssh $RPROXY -- "sudo tee /etc/sshd_config" < etc/sshd_config'
echo
echo 'After starting the car server, you can now connect to the car at http://$RPROXY:9999/car/'
echo 'For HTTPS and authentication, set up an nginx reverse proxy on $RPROXY (see etc/remote_nginx.conf)'
echo
echo "To start the car server"
echo "-----------------------"
echo "sudo systemctl start car"
echo
echo "Open http://raspberrypi/car/"
echo
exit
