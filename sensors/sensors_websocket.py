#!/usr/bin/env python

import asyncio
import json
import websockets
from pathlib import Path
import threading
from multiprocessing import Process, Value, Array
import sys
import signal
import time

import Adafruit_DHT

import RPi.GPIO as gpio

import VL53L1X
from ctypes import CDLL, CFUNCTYPE, POINTER, c_int, c_uint, pointer, c_ubyte, c_uint8, c_uint32, Structure

class VL53L1_UserZone(Structure):
    _fields_ = [("x_centre", c_ubyte),
                ("y_centre", c_ubyte),
                ("width", c_ubyte),
                ("height", c_ubyte)]

def set_zone(dev, x0, y0, w, h):
    roi = VL53L1_UserZone(x0, y0, w, h)
    roi_p = pointer(roi)
    return VL53L1X._TOF_LIBRARY.VL53L1_set_user_zone(dev, roi_p)

gpio.setmode(gpio.BCM)

temperature_sensor = Adafruit_DHT.DHT11
temperature_pin = 14

pir_pin = 22

tof_power_pin = 4

connection_count = 0
active_file_path = Path("/var/run/car/sensors.active")

def pirThread(pir_state):
    gpio.setmode(gpio.BCM)
    gpio.setup(pir_pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    while True:
        gpio.wait_for_edge(pir_pin, gpio.RISING, timeout=500)
        if gpio.input(pir_pin):
            pir_state[0] = 1
            pir_state[1] = time.time()
            while gpio.input(pir_pin):
                gpio.wait_for_edge(pir_pin, gpio.FALLING, timeout=500)
                if not gpio.input(pir_pin):
                    pir_state[0] = 0
                    pir_state[1] = time.time()

def temperatureThread(temperature_state):
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(temperature_sensor, temperature_pin)
        if humidity is not None and temperature is not None:
            temperature_state[0] = temperature
            temperature_state[1] = humidity
            temperature_state[2] = time.time()
        time.sleep(2)

def distanceCleanup(signal, frame):
    global tof, tof_power_pin
    tof.stop_ranging()
    gpio.output(tof_power_pin, gpio.LOW)
    gpio.cleanup()
    sys.exit(0)

def distanceThread(distance_state):
    global tof, tof_power_pin
    signal.signal(signal.SIGINT, distanceCleanup)

    gpio.setmode(gpio.BCM)
    gpio.setup(tof_power_pin, gpio.OUT)
    gpio.output(tof_power_pin, gpio.HIGH)
    tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
    tof.open()
    #status = set_zone(tof._dev, 12, 3, 3, 5)
    tof.start_ranging(3)
    VL53L1X._TOF_LIBRARY.VL53L1_SetXTalkCompensationEnable(tof._dev, 1)
    VL53L1X._TOF_LIBRARY.VL53L1_SetMeasurementTimingBudgetMicroSeconds(tof._dev, 10000)
    VL53L1X._TOF_LIBRARY.VL53L1_SetInterMeasurementPeriodMilliSeconds(tof._dev, 14)
    while True:
        distance_state[0] = tof.get_distance()
        distance_state[1] = time.time()
        time.sleep(0.025)

pir_state = Array('d', [0, time.time()])
pir_thread = Process(target=pirThread, args=(pir_state,))
pir_thread.start()

temperature_state = Array('d', [0, 0, time.time()])
temperature_thread = Process(target=temperatureThread, args=(temperature_state,))
temperature_thread.start()

distance_state = Array('d', [0, time.time()])
distance_thread = Process(target=distanceThread, args=(distance_state,))
distance_thread.start()

async def sensorTelemetry(websocket, path):
    global connection_count, active_file_path
    global pir_state, temperature_state, distance_state
    connection_count += 1
    try:
        active_file_path.touch(mode=0o660, exist_ok=True)
    except:
        print("Error touching", active_file_path, sys.exc_info()[0])
    try:
        last_update = time.time()
        await websocket.send(json.dumps({
            'person_detected': pir_state[0],
            'temperature': temperature_state[0],
            'humidity': temperature_state[1],
            'distance': distance_state[0],
            'timestamp': last_update
        }))
        while True:
            t = last_update
            if distance_state[1] > last_update:
                await websocket.send("{\"distance\": %d, \"timestamp\": %f}" %
                                     (distance_state[0], distance_state[1]))
                t = max(t, distance_state[1])
            if temperature_state[2] > last_update:
                await websocket.send("{\"temperature\": %.1f, \"humidity\": %.1f, \"timestamp\": %f}" %
                                     (temperature_state[0], temperature_state[1], temperature_state[2]))
                t = max(t, temperature_state[2])
            if pir_state[1] > last_update:
                await websocket.send("{\"person_detected\": %f, \"timestamp\": %f}" %
                                     (pir_state[0], pir_state[1]))
                t = max(t, pir_state[1])
            last_update = max(last_update, t)
            time.sleep(0.01)
    finally:
        connection_count -= 1
        if connection_count == 0:
            try:
                active_file_path.unlink()
            except:
                print("Error unlinking", active_file_path, sys.exc_info()[0])
        print("Connection closed")


try:
    try:
        active_file_path.unlink()
        print("Deleted", active_file_path)
    except:
        print("")

    start_server = websockets.serve(sensorTelemetry, '0.0.0.0', 5677, compression=None)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

finally:
    try:
        active_file_path.unlink()
    except:
        print("Error unlinking", active_file_path, sys.exc_info()[0])
