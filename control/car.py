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
    pwm_front_lights_left = GPIO.PWM(front_lights_left_pin, 1000)
    pwm_front_lights_left.start(0)
    pwm_front_lights_right = GPIO.PWM(front_lights_right_pin, 1000)
    pwm_front_lights_right.start(0)
    pwm_rear_lights = GPIO.PWM(rear_lights_pin, 1000)
    pwm_rear_lights.start(0)

    #GPIO.setup(power_pin, GPIO.OUT)

    GPIO.setup(left_pin, GPIO.OUT)
    pwm_left = GPIO.PWM(left_pin, 100)
    pwm_left.start(0)

    GPIO.setup(right_pin, GPIO.OUT)
    pwm_right = GPIO.PWM(right_pin, 100)
    pwm_right.start(0)

    GPIO.setup(fwd_pin, GPIO.OUT)
    pwm_fwd = GPIO.PWM(fwd_pin, 100)
    pwm_fwd.start(0)

    GPIO.setup(back_pin, GPIO.OUT)
    pwm_back = GPIO.PWM(back_pin, 100)
    pwm_back.start(0)



def apply_state(state):
    global pwm_fwd, pwm_back
    global pwm_left, pwm_right
    global pwm_front_lights_left, pwm_front_lights_right, pwm_rear_lights

    pwm_rear_lights.ChangeDutyCycle(state['rear_lights'])
    blink = state['blink']

    if blink == -1:
        pwm_front_lights_left.ChangeFrequency(1)
        pwm_front_lights_left.ChangeDutyCycle(50)
        pwm_front_lights_right.ChangeFrequency(120)
        pwm_front_lights_right.ChangeDutyCycle(state['front_lights'])
    elif blink == 1:
        pwm_front_lights_left.ChangeFrequency(120)
        pwm_front_lights_left.ChangeDutyCycle(state['front_lights'])
        pwm_front_lights_right.ChangeFrequency(1)
        pwm_front_lights_right.ChangeDutyCycle(50)
    else:
        pwm_front_lights_left.ChangeFrequency(120)
        pwm_front_lights_left.ChangeDutyCycle(state['front_lights'])
        pwm_front_lights_right.ChangeFrequency(120)
        pwm_front_lights_right.ChangeDutyCycle(state['front_lights'])

    pwm_fwd.ChangeDutyCycle(state['fwd'] * state['pwm_move'])
    pwm_back.ChangeDutyCycle(state['back'] * state['pwm_move'])
    pwm_left.ChangeDutyCycle(state['left'] * state['pwm_steer'])
    pwm_right.ChangeDutyCycle(state['right'] * state['pwm_steer'])


def cleanup():
    global pwm_fwd, pwm_back
    global pwm_left, pwm_right
    global pwm_front_lights_left, pwm_front_lights_right, pwm_rear_lights

    pwm_fwd.ChangeDutyCycle(0)
    pwm_fwd.stop()
    pwm_back.ChangeDutyCycle(0)
    pwm_back.stop()
    pwm_left.ChangeDutyCycle(0)
    pwm_left.stop()
    pwm_right.ChangeDutyCycle(0)
    pwm_right.stop()

    pwm_front_lights_left.ChangeDutyCycle(0)
    pwm_front_lights_left.stop()
    pwm_front_lights_right.ChangeDutyCycle(0)
    pwm_front_lights_right.stop()
    pwm_rear_lights.ChangeDutyCycle(0)
    pwm_rear_lights.stop()

    GPIO.cleanup()
