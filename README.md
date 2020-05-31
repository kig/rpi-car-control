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

After starting the car control app with `sudo systemctl start car`, you can connect to `http://raspberrypi/car/` and play with the controls web page.

The car control app is installed in `/opt/rpi-car-control`.

To use a SSH tunnel server, edit `/etc/rpi-car-control/env.sh` and change the line `RPROXY_SERVER=` to `RPROXY_SERVER=my.server`.

With the SSH tunnel, you can access the car from `http://my.server:9999/car/`. Best to firewall this port and add a HTTPS reverse proxy that points to it. Look at `etc/remote_nginx.conf` for a snippet that sets up an authenticated NGINX reverse proxy on the remote server. (Run `htpasswd -c /etc/nginx/car_htpasswd my_username` to create the password file.)

## Configuration

See `/etc/rpi-car-control/env.sh` for settings.

```bash
# SSH tunnel reverse proxy
RPROXY_SERVER=my.server

# One of v4l2-mjpeg, v4l2-raw, raspivid
VIDEO_MODE=v4l2-raw

# Which camera to use in the v4l2 modes
V4L2_DEVICE=/dev/video2

# Video settings
VIDEO_WIDTH=480
VIDEO_HEIGHT=270
VIDEO_FPS=60

VIDEO_ROTATION=0
```

## Controls

![Controls HUD](https://github.com/kig/rpi-car-control/raw/master/doc/controls.png)

The circle on the left is the accelerator indicator, and the circle on the right is the steering indicator. The bar in the bottom middle is the reversing distance indicator. The sensor data readout is at top left. The little square at the bottom right toggles the full screen mode.

The controls are defined near the bottom of `html/main.js`.

### Touch controls

* Use left thumb to accelerate and reverse, right thumb to steer.

### Keyboard controls

* Use arrow keys to drive. 
* The numbers `1`-`4` control front lights intensity and `0` turns the rear lights on and off. 
* The `z` key blinks the left front light, the `c` key blinks the right front light and the `x` key turns off the blinkers.

## Requirements

The app is very modular, so you can run the app without an actual car or camera. And just play with a web page with controls that do nothing.

If you wire up the motors, you should be able to drive. If you wire up the lights, they should light up.

Wire up the sensors and you should start seeing sensor data in the HUD.

Add a camera and you'll see a live video stream.

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
* Use RaspiCam or a V4L2 USB webcam, either with raw video (eats CPU) or camera-supplied MJPEG

## Disabled

* Bluetooth speaker pairing for playing audio.
* Stream car microphone to the browser.
* Speak to the car from the browser by sending audio with Web Audio API.
* WebRTC call between browser and car.

## In progress

* PoseNet with Coral USB accelerator for "point and I'll drive there"

## Wanted

* OMX JPEG encoder for raw video cameras
* SLAM and "click on a map position to drive there"
* Good small microphone + speaker solution
* Small display to do two-way video calls
* Non-sucky camera mount (duct tape doesn't really work)
* Power car and computer from one battery
* Automatic wireless charging when battery is low
* Shutdown when battery critical
* Speech controls

## Customize

Take a look at `run.sh` first. It starts the web server and optionally the reverse proxy tunnel. The web server is in `web/web_server.py` and starts up `bin/start_control_server.sh` and `bin/start_server.sh` when needed. The sensors are controlled by `sensors/sensors_websocket.py`, and the car controls are in `control/car_websockets.py`. For video streaming, have a look at `video/start_stream.sh`. The HUD is in `html/`, see `html/main.js` for the car controls and how the video and sensor data are streamed.

## License

MIT

Ilmari Heikkinen &copy; 2020
