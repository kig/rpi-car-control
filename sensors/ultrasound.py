import time
import RPi.GPIO as GPIO
import datetime as dt
import math
import sys
from multiprocessing import Process, Value, Array

import Adafruit_DHT
import speed_of_sound

import kalman

x_est, error_est = kalman.kalman(0.02, 0.02, 0.01, 0.005, 0.0001)

c_in_us = Value('d', speed_of_sound.calculate_c(22, 50) / 1e6)

def update_c_in_us(c_in_us):
    dht_sensor = Adafruit_DHT.DHT11
    dht_pin = 14
    initialized = False

    while True:
        relative_humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, dht_pin)
        if relative_humidity is not None and temperature is not None:
            c = speed_of_sound.calculate_c(temperature, relative_humidity) / 1e6
            if not initialized:
                x_est, error_est = kalman.kalman(c, c, 0.1, 0.05, 0.001)
                initialized = True
            else:
                x_est, error_est = kalman.kalman(c, x_est, error_est, 0.05, 0.001)
            c_in_us.value = x_est
            print('Temp=%.1fC  Humidity=%.1f%%  Mach 1=%.1fm/s                                   ' % (temperature, relative_humidity, c_in_us.value * 1e6))
        time.sleep(2)


temp_update = Process(target=update_c_in_us, args=(c_in_us,))
temp_update.start()

try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(2, GPIO.OUT)
    GPIO.setup(3, GPIO.IN)
    GPIO.output(2, GPIO.LOW)

    max_wait_time = 120000
    t_prev = dt.datetime.now()

    mean = 0.2
    variance = 0.005

    while True:
        t_start = dt.datetime.now()

        # Wait for the ping cap to charge
        time.sleep(0.01)

        # Send the trigger signal for 10us
        GPIO.output(2, GPIO.HIGH)
        time.sleep(0.00001)
        GPIO.output(2, GPIO.LOW)

        # Time how long it takes for the echo signal to arrive
        GPIO.wait_for_edge(3, GPIO.RISING, timeout = int(max_wait_time / 1000))
        t0 = dt.datetime.now()
        GPIO.wait_for_edge(3, GPIO.FALLING, timeout = int(max_wait_time / 1000))
        t1 = dt.datetime.now()

        # Echo timed out
        if (t1 - t0).microseconds >= max_wait_time:
            sys.stdout.buffer.write(b'Distance: inf+                                                              \r')
            sys.stdout.buffer.flush()
            continue

        # Calculate and print out the distance and sampling rate
        t2 = (t1 - t0).microseconds
        distance = t2 * 0.5 * c_in_us.value
        #delta = distance - mean

        #f = 0.05
        
        #mean = (1-f) * mean + f * distance
        #variance = (1-f) * variance + f * delta * delta
        #process_variance = 0.001

        x_est, error_est = kalman.kalman(distance, x_est, error_est, 0.005, 0.00001)
        
        hz = 1000000 / ((t_start - t_prev).microseconds)
        #sys.stdout.buffer.write(b'Distance: %.3f+-%.3f m (Raw: %.3f m, %d Hz, Mean: %.3f m, SD: %.3f)               \r' % (x_est, error_est, distance, hz, mean, math.sqrt(variance)))
        sys.stdout.buffer.write(b'%.3f m        \r' % (x_est,))
        sys.stdout.buffer.flush()
        t_prev = t_start

finally:
    GPIO.cleanup()
