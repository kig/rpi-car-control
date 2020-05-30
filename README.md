# rpi-car-control

Use a Raspberry Pi to drive an RC car from a web page.

## How does it work?

Open up a cheap RC toy car. Connect the motors to a Raspberry Pi. Add a camera. Run a web server on the Raspberry Pi that controls the car.

In more detail, you need to replace the car PCB with a motor controller board (say, a tiny cheap MX1508 module). Then solder the motors and the car battery pack to the motor controller. Solder M-F jumper cables to the motor controller's control connectors. Plug the other end of the jumpers to the Raspberry Pi GPIOs. Now you can control the motors from the Raspberry Pi.

Expose the Raspberry Pi camera as an MJPEG stream so that you can directly view it as an IMG on the browser. This is the easiest low latency, low CPU, high quality streaming format.

If the car has lights, you can drive them from the GPIOs as well (either directly or via a proper LED controller). Add a bunch of sensors to the car for the heck of it. I've got a tiny VL53L1X ToF laser-ranging sensor as a reversing radar, and a DHT temperature and humidity sensor. There's code in the repo to hook up an ultrasonic range finder too (it can even use the DHT sensor to calculate the speed of sound for given temperature and humidity - and has a Kalman filter of sorts, so you can reach ~mm accuracy), and some bits and bops for using a PIR sensor.

There was also a microphone input and playback either through wired speakers or to a Bluetooth speaker, but that's not enabled at the moment. There was also a WebRTC-based streaming solution for doing 2-way video calls, but that was such a pain I gave up on it. I was using RWS which is pretty easy to set up, but the STUN/TURN stuff was tough.

Add a USB battery pack to power the Raspberry Pi and you're about done. If you're feeling adventurous, you could use a 5V step-up/step-down regulator to run the Raspberry Pi directly from the car batteries.

## Install

```bash
raspi-config # Enable I2C to use the VL53L1X sensor
sh install.sh
```

The install script installs the car service and its dependencies. This is best done on a fresh install of Raspbian. The install script overwrites NGINX's default site configuration.

The car control app is installed in `/opt/rpi-car-control`.

To use a SSH tunnel server, edit `/etc/rpi-car-control/env.sh` and change the line `RPROXY_SERVER=` to `RPROXY_SERVER=my.server.address`.

## Wiring

See `control/car.py` and `sensors/sensors_websocket.py` for the pin definitions. The VCC and GND connections have been left out. Just remember to use the correct voltage when wiring those.

<table>
<tr><th>Component</th><th>GPIO</th><th>Notes</th></tr>

<tr><td>Motor forward (A)</td><td>17</td><td></td></tr>
<tr><td>Motor backward (B)</td><td>27</td><td></td></tr>
<tr><td>Steering left (A)</td><td>24</td><td></td></tr>
<tr><td>Steering right (B)</td><td>23</td><td></td></tr>

<tr><td>Left headlight</td><td>5</td><td>The headlights turn on when you connect</td></tr>
<tr><td>Right headlight</td><td>6</td><td>They can also blink a turning signal</td></tr>

<tr><td>Rear lights</td><td>13</td><td>Rear lights light up when you reverse</td></tr>

<tr><td>Power PWM</td><td>12</td><td>Disabled, for use with L298N</td></tr>

<tr><td>DHT11 signal</td><td>14</td><td></td></tr>
<tr><td>PIR signal</td><td>22</td><td></td></tr>
<tr><td>VL53L1X power</td><td>4</td><td>Use a GPIO and you can turn it off when not in use</td></tr>
<tr><td>VL53L1X SDA</td><td>2</td><td>I2C bus 1</td></tr>
<tr><td>VL53L1X SCL</td><td>3</td><td>I2C bus 1</td></tr>
</table>

## Features

* FPV stream web page with keyboard & touch controls to drive the car, along with a reversing distance indicator and a thermometer.
* Low latency video stream for driving (down to 50 ms glass-to-glass when using a 90 Hz camera and a 240 Hz display.)
* Bunch of websocket servers to send out sensor data and receive car controls.
* Nginx reverse proxy config to tie all the servers together.
* Systemd service to start the car control server on boot.
* SSH tunnel to a remote control server to drive the car from anywhere.
* Low-power tweaks to increase battery life (disables HDMI, Ethernet and USB.)

## Disabled

* Bluetooth speaker pairing for playing audio.
* Stream car microphone to the browser.
* Speak to the car from the browser by sending audio with Web Audio API.
* WebRTC call between browser and car.

## In progress

* PoseNet with Coral USB accelerator for "point and I'll drive there"

## Wanted

* SLAM and "click on a map position to drive there"
* Good small microphone + speaker solution
* Small display to do two-way video calls
* Non-sucky camera mount (duct tape doesn't really work)
* Power car and computer from one battery
* Automatic wireless charging when battery is low
* Shutdown when battery critical
* Speech controls

## Customize

Take a look at `run.sh` first. It starts the web server and optionally the reverse proxy tunnel. The web server is in `web/web_server.py` and starts up `bin/start_control_server.sh` and `bin/start_server.sh` when needed. The sensors are controlled by `sensors/sensors_websocket.py`, and the car controls are in `control/car_websockets.py`. For video streaming, have a look at `video/start_stream.sh`.

## License

MIT

Ilmari Heikkinen &copy; 2020
