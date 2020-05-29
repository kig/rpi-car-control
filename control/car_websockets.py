#!/usr/bin/env python

import asyncio
import json
import websockets
from pathlib import Path
import threading
import sys
import time

import car

gpio_state = {
    'left': 0,
    'right': 0,

    'fwd': 0,
    'back': 0,

    'pwm_steer': 0,
    'pwm_move': 0,

    'front_lights': 0,
    'blink': 0,
    'rear_lights': 0
}

def handleControl(message):
    global gpio_state
    obj = json.loads(message)

    gpio_state['pwm_steer'] = min(100, max(0, abs(obj['steer'])))
    gpio_state['pwm_move'] = min(100, max(0, abs(obj['move'])))

    gpio_state['left'] = 0
    gpio_state['right'] = 0

    gpio_state['front_lights'] = obj['front_lights']
    gpio_state['blink'] = obj['blink']
    gpio_state['rear_lights'] = obj['rear_lights']

    if obj['steer'] < 0:
        gpio_state['left'] = 1
    elif obj['steer'] > 0:
        gpio_state['right'] = 1

    gpio_state['fwd'] = 0
    gpio_state['back'] = 0

    if obj['move'] > 0:
        gpio_state['fwd'] = 1
    elif obj['move'] < 0:
        gpio_state['back'] = 1

    car.apply_state(gpio_state)

connection_count = 0
active_file_path = Path("/var/run/car/websocket.active")

def controlResetThread(control, done):
    while True:
        # kill controls if idle for more than half sec
        if not control['triggered'] and control['last_control'] + 0.5 < time.time():
            handleControl('{"move":0,"steer":0,"front_lights":0,"blink":0,"rear_lights":0}')
            control['triggered'] = True
        if done.wait(0.1):
            handleControl('{"move":0,"steer":0,"front_lights":0,"blink":0,"rear_lights":0}')
            print("Ending control reset thread for connection")
            break


async def carControl(websocket, path):
    global gpio_state, connection_count, active_file_path
    control = { 'last_control': 0, 'triggered': False }
    connection_count += 1
    try:
        active_file_path.touch(mode=0o660, exist_ok=True)
    except:
        print("Error touching", active_file_path, sys.exc_info()[0])
    try:
        done = threading.Event()
        thread = threading.Thread(target=controlResetThread, args=(control, done))
        thread.daemon = True
        thread.start()
        await websocket.send(json.dumps(gpio_state))
        async for message in websocket:
            control['last_control'] = time.time()
            control['triggered'] = False
            if message != '1':
                handleControl(message)
                await websocket.send(json.dumps(gpio_state))
    finally:
        connection_count -= 1
        if connection_count == 0:
            try:
                active_file_path.unlink()
            except:
                print("Error unlinking", active_file_path, sys.exc_info()[0])
        done.set()
        thread.join()
        print("Connection closed")


try:
    try:
        active_file_path.unlink()
        print("Deleted", active_file_path)
    except:
        print("")
    car.init()

    start_server = websockets.serve(carControl, '0.0.0.0', 5678, compression=None)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

finally:
    try:
        active_file_path.unlink()
    except:
        print("Error unlinking", active_file_path, sys.exc_info()[0])
    car.cleanup()
