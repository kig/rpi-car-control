import RPi.GPIO as GPIO
import time

front_lights_left_pin = 5
front_lights_right_pin = 6

rear_lights_pin = 13

power_pin = 12

fwd_pin = 17
back_pin = 27

left_pin = 24
right_pin = 23

pwm_fwd = None
pwm_back = None
pwm_left = None
pwm_right = None

pwm_front_lights_left = None
pwm_front_lights_right = None
pwm_rear_lights = None

blink = 0

def init():
    global fwd_pin, back_pin
    global pwm_fwd, pwm_back
    global left_pin, right_pin
    global pwm_left, pwm_right
    global front_lights_left_pin, front_lights_right_pin
    global rear_lights_pin, pwm_front_lights_left, pwm_front_lights_right, pwm_rear_lights

    GPIO.setmode(GPIO.BCM)

    GPIO.setup(front_lights_left_pin, GPIO.OUT)
    GPIO.setup(front_lights_right_pin, GPIO.OUT)
    GPIO.setup(rear_lights_pin, GPIO.OUT)
    pwm_front_lights_left = GPIO.PWM(front_lights_left_pin, 120)
    pwm_front_lights_right = GPIO.PWM(front_lights_right_pin, 120)
    pwm_rear_lights = GPIO.PWM(rear_lights_pin, 120)

    #GPIO.setup(power_pin, GPIO.OUT)

    GPIO.setup(left_pin, GPIO.OUT)
    pwm_left = GPIO.PWM(left_pin, 100)

    GPIO.setup(right_pin, GPIO.OUT)
    pwm_right = GPIO.PWM(right_pin, 100)

    GPIO.setup(fwd_pin, GPIO.OUT)
    pwm_fwd = GPIO.PWM(fwd_pin, 100)

    GPIO.setup(back_pin, GPIO.OUT)
    pwm_back = GPIO.PWM(back_pin, 100)

def changeDutyCycle(pwm, dc, hz):
    if dc == 0:
        pwm.stop()
    else:
        pwm.ChangeFrequency(hz)
        pwm.start(dc)

def apply_state(state):
    global pwm_fwd, pwm_back
    global pwm_left, pwm_right
    global pwm_front_lights_left, pwm_front_lights_right, pwm_rear_lights

    changeDutyCycle(pwm_rear_lights, state['rear_lights'], 120)
    blink = state['blink']

    if blink == -1:
        changeDutyCycle(pwm_front_lights_left, 50, 1)
        changeDutyCycle(pwm_front_lights_right, state['front_lights'], 120)
    elif blink == 1:
        changeDutyCycle(pwm_front_lights_left, state['front_lights'], 120)
        changeDutyCycle(pwm_front_lights_right, 50, 1)
    else:
        changeDutyCycle(pwm_front_lights_left, state['front_lights'], 120)
        changeDutyCycle(pwm_front_lights_right, state['front_lights'], 120)

    changeDutyCycle(pwm_fwd, state['fwd'] * state['pwm_move'], 100)
    changeDutyCycle(pwm_back, state['back'] * state['pwm_move'], 100)
    changeDutyCycle(pwm_left, state['left'] * state['pwm_steer'], 100)
    changeDutyCycle(pwm_right, state['right'] * state['pwm_steer'], 100)


def cleanup():
    global pwm_fwd, pwm_back
    global pwm_left, pwm_right
    global pwm_front_lights_left, pwm_front_lights_right, pwm_rear_lights

    pwm_fwd.stop()
    pwm_back.stop()
    pwm_left.stop()
    pwm_right.stop()

    pwm_front_lights_left.stop()
    pwm_front_lights_right.stop()
    pwm_rear_lights.stop()

    GPIO.cleanup()
