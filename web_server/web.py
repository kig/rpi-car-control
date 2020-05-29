from http.server import HTTPServer, SimpleHTTPRequestHandler
from os import system, path, chdir
from subprocess import DEVNULL, PIPE
import subprocess

import threading
import time

import signal
signal.signal(signal.SIGCHLD, signal.SIG_IGN)

scriptDir = path.dirname(path.realpath(__file__))
htmlDir = path.realpath(path.join(scriptDir, "..", "html"))

serverStartTimeout = 10

streamServerProcess = None
serverStartTime = 0

controlServerProcess = None

def startServer():
    global streamServerProcess, serverStartTime, serverStartTimeout
    streamServerProcess = subprocess.Popen([path.realpath(path.join(scriptDir, "..", "bin", "start_server.sh"))])
    serverStartTime = time.time()

def stopServer():
    global streamServerProcess, serverStartTime, serverStartTimeout
    streamStopProcess = subprocess.Popen([path.realpath(path.join(scriptDir, "..", "bin", "stop_server.sh"))])
    streamServerProcess.wait(1)

    if streamServerProcess.poll() != None:
        streamServerProcess = None


def startControlServer():
    global controlServerProcess
    controlServerProcess = subprocess.Popen([path.realpath(path.join(scriptDir, "..", "bin", "start_control_server.sh"))])

def stopControlServer():
    global controlServerProcess
    controlStopProcess = subprocess.Popen([path.realpath(path.join(scriptDir, "..", "bin", "stop_control_server.sh"))])
    controlServerProcess.wait(1)

    if controlServerProcess.poll() != None:
        controlServerProcess = None


startControlServer()

chdir(htmlDir)

class CarHTTPRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        global streamServerProcess, serverStartTime, serverStartTimeout, controlServerProcess

        if streamServerProcess != None and streamServerProcess.poll() != None:
            streamServerProcess = None

        if self.path == "/" and controlServerProcess == None or controlServerProcess.poll() != None:
            print("GET /: Control server down, starting it")
            startControlServer()

        if self.path == "/" and streamServerProcess == None:
            print("GET /: Streaming server down, starting it")
            startServer()

        SimpleHTTPRequestHandler.do_GET(self)

def serverManagerThread():
    global streamServerProcess, serverStartTime, serverStartTimeout, controlServerProcess
    while True:
        # If the control server is down, bring it up
        if controlServerProcess == None or controlServerProcess.poll() != None:
            print("Control server down, starting it")
            startControlServer()
            time.sleep(1)

        # If the control server is active, bring the streaming server up
        if (
                path.isfile("/var/run/car/websocket.active")
                and not path.isfile("/var/run/car/server.pid")
                and streamServerProcess == None
                and time.time() > serverStartTime + serverStartTimeout
        ):
            print("Controls active, starting streaming server")
            startServer()

        # If the control server is inactive, shut down the streaming server
        if (
                not path.isfile("/var/run/car/websocket.active")
                and path.isfile("/var/run/car/server.pid")
                and streamServerProcess != None
                and time.time() > serverStartTime + serverStartTimeout
        ):
            print("Controls inactive, stopping streaming server")
            stopServer()

        time.sleep(5)

thread = threading.Thread(target=serverManagerThread, args=())
thread.daemon = True
thread.start()

address = ('', 8000)
httpd = HTTPServer(address, CarHTTPRequestHandler)
httpd.serve_forever()
