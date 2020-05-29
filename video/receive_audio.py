#!/usr/bin/env python

import RPi.GPIO as GPIO

import asyncio
import json
import websockets
from subprocess import Popen, DEVNULL, PIPE

import time

import sys

def writeOutAudio(player, message):
    #sys.stderr.buffer.write(bytes("Received " + str(len(message)) + " bytes\n", 'ascii'))
    player.stdin.write(message)
    player.stdin.flush()

async def audioListener(websocket, path):
    try:
        player = Popen(
            # 'aplay -c 1 -f S16_LE -r 44100 -B 10000 -'.split(" "),
            # 'play --buffer 441 -r 44100 -b 16 -c 1 -e signed -t raw -'.split(" "),
            'play -t mp3 -'.split(" "),
            stdin=PIPE, bufsize=0)
        startTime = time.time()
        await websocket.send("heartbeat")
        async for message in websocket:
            if (time.time() > startTime+3):
                writeOutAudio(player, message)
            await websocket.send("heartbeat")
    finally:
        player.kill()


start_server = websockets.serve(audioListener, '0.0.0.0', 5679)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

