import math

def kalman(new_measurement, estimate, error, variance, process_variance):
    error += process_variance

    speed = error / (error + variance)
    estimate = estimate + (new_measurement - estimate) * speed
    error = (1 - speed) * error

    return estimate, error

