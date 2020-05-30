if (window.JSMpeg) {
    var canvas = document.getElementById('video-canvas');
    var url = document.location.toString().replace(/^http/, 'ws') + 'video-out';
    var player = new JSMpeg.Player(url, { canvas: canvas });
} else {
    var img = document.getElementById('video-canvas');
    img.style.opacity = 'none';
    var src = img.src;
    setInterval(function () {
        if (img.naturalWidth === 0) {
            img.style.display = 'none';
            img.src = src + '?' + Date.now();
        } else {
            img.style.display = 'inline-block';
        }
    }, 1000);
}

var sensorsWs = null;

var connectSensors = function () {
    sensorsWs = new WebSocket(document.location.toString().replace(/^http/, 'ws') + "sensors");
    var ws = sensorsWs;

    ws.onopen = function (event) {
        img.src = src + '?' + Date.now();
        ws.onmessage = function (event) {
            var obj = JSON.parse(event.data);
            updateSensorsState(obj);
        };
    };

    ws.onclose = function (event) {
        console.log('Socket is closed. Reconnect will be attempted in 0.5 seconds.', event.reason);
        setTimeout(function () {
            connectSensors();
        }, 500);
    };

    ws.onerror = function (event) {
        ws.close();
    };
}

var ws = null;

var connect = function () {
    ws = new WebSocket(document.location.toString().replace(/^http/, 'ws') + "control");

    ws.onopen = function (event) {
        img.src = src + '?' + Date.now();
        ws.onmessage = function (event) {
            var obj = JSON.parse(event.data);
            drawControlsState(obj);
        };
    };

    ws.onclose = function (event) {
        console.log('Socket is closed. Reconnect will be attempted in 0.1 second.', event.reason);
        setTimeout(function () {
            connect();
        }, 100);
    };

    ws.onerror = function (event) {
        ws.close();
    };

};

var lastControlsState = null;

var controlCanvas = document.createElement('canvas');
controlCanvas.id = 'control-canvas';

var ctx = controlCanvas.getContext('2d');

var controlR = 0.3;
var controlTop = 0.72;
var controlMargin = 0.15;

var sensorsState = {
    person_detected: false,
    temperature: 0,
    humidity: 0,
    distance: 0,
    timestamp: 0
};

function updateSensorsState(obj) {
    for (var i in obj) {
        sensorsState[i] = obj[i];
    }
    drawControlsState(lastControlsState);
}

function kalman(new_measurement, estimateAndError, process_variance) {
    var estimate = estimateAndError.estimate;
    var error = estimateAndError.error;
    var variance = estimateAndError.variance * new_measurement;

    error += process_variance;

    var speed = error / (error + variance);
    estimate = estimate + (new_measurement - estimate) * speed;
    error = (1 - speed) * error;

    estimateAndError.estimate = estimate;
    estimateAndError.error = error;
}

function getReverseColor(d) {
    if (d < 300) {
        var f = Math.max(0, d / 300);
        var h = f * 60;
        return `hsl(${h}, 100%, 50%)`;
    } else if (d < 600) {
        var f = (d - 300) / 300;
        var h = f * 30 + 60;
        return `hsl(${h}, 100%, 50%)`;
    } else if (d < 800) {
        var f = (d - 600) / 200;
        var a = Math.pow(1 - f, 2);
        return `hsla(90, 100%, 50%, ${a})`;
    }
    return 'transparent';
}

var distanceK = { estimate: 1000, error: 100, variance: 0.03 };

function drawSensorsState() {
    ctx.clearRect(0, 0, 400, 120);
    var mid = ctx.canvas.width / 2;
    var bottom = ctx.canvas.height;
    kalman(sensorsState.distance, distanceK, 3);

    ctx.clearRect(mid - 200, bottom - 120, 400, 120);
    ctx.save();
    {
        ctx.fillStyle = 'white';
        ctx.fillText("Distance: " + Math.round(distanceK.estimate) + " mm", 20, 40);
        ctx.fillText("Temperature: " + sensorsState.temperature + " C", 20, 60);
        ctx.fillText("Humidity: " + sensorsState.humidity + "%", 20, 80);
        ctx.fillText("Motion: " + sensorsState.person_detected, 20, 100);

        ctx.translate(mid, bottom);
        ctx.strokeStyle = getReverseColor(distanceK.estimate - 60);
        ctx.beginPath();
        ctx.moveTo(-180, -100);
        ctx.bezierCurveTo(-120, -60, -60, -60, 0, -60);
        ctx.bezierCurveTo(60, -60, 120, -60, 180, -100);
        ctx.lineWidth = 20;
        ctx.stroke();
    }
    ctx.restore();
}

function drawControlsState(obj) {

    lastControlsState = obj;

    ctx.clearRect(0, 0, controlCanvas.width, controlCanvas.height);
    drawSensorsState();

    if (obj) {
        ctx.save();
        {
            ctx.fillStyle = 'white';
            ctx.strokeStyle = '#ccc';
            ctx.lineWidth = 10 / 100;
            ctx.translate(controlCanvas.width * controlMargin, controlCanvas.height * controlTop);
            ctx.scale(0.5 * controlCanvas.height * controlR, 0.5 * controlCanvas.height * controlR);
            ctx.beginPath();
            ctx.arc(0, 0, 1, 0, Math.PI * 2, true);
            ctx.clip();
            ctx.fillRect(-1, -0.2, 2, 0.4);
            ctx.globalAlpha = 0.5;
            ctx.fillRect(-1, 0, 2, -(obj.fwd - obj.back) * obj.pwm_move * 0.01);
            ctx.arc(0, 0, 1, 0, Math.PI * 2, true);
            ctx.stroke();
        }
        ctx.restore();

        ctx.save();
        {
            ctx.fillStyle = 'white';
            ctx.strokeStyle = '#ccc';
            ctx.lineWidth = 10 / 100;
            ctx.translate(controlCanvas.width * (1 - controlMargin), controlCanvas.height * controlTop);
            ctx.scale(0.5 * controlCanvas.height * controlR, 0.5 * controlCanvas.height * controlR);
            ctx.beginPath();
            ctx.arc(0, 0, 1, 0, Math.PI * 2, true);
            ctx.clip();
            ctx.fillRect(-0.2, -1, 0.4, 2);
            ctx.globalAlpha = 0.5;
            ctx.fillRect(0, -1, (obj.right - obj.left) * obj.pwm_steer * 0.01, 2);
            ctx.arc(0, 0, 1, 0, Math.PI * 2, true);
            ctx.stroke();
        }
        ctx.restore();
    }
};

document.body.appendChild(controlCanvas);

var controlState = {
    steer: 0,
    move: 0,
    blink: 0,
    front_lights: 100,
    rear_lights: 20
};

var controlSignal = {
    steer: 0,
    move: 0,
    blink: 0,
    front_lights: 0,
    rear_lights: 0
};

var keys = {};

var heartbeat = '1';
var lastHeartbeat = Date.now();

drawControlsState({
    left: controlSignal.steer < 0 ? 1 : 0,
    right: controlSignal.steer > 0 ? 1 : 0,
    pwm_steer: Math.abs(controlSignal.steer),
    back: controlSignal.move < 0 ? 1 : 0,
    fwd: controlSignal.move > 0 ? 1 : 0,
    pwm_move: Math.abs(controlSignal.move)
});

setInterval(function () {
    if (ws.readyState !== WebSocket.OPEN) {
        return;
    }
    var changed = false;
    for (var i in controlSignal) {
        if (controlSignal[i] !== controlState[i]) {
            changed = true;
        }
    }
    if (changed) {
        controlSignal.front_lights = controlState.front_lights
        controlSignal.rear_lights = controlState.rear_lights
        controlSignal.blink = controlState.blink

        controlSignal.steer += (controlState.steer - controlSignal.steer) * 0.05;
        controlSignal.move += (controlState.move - controlSignal.move) * 0.2;
        if (Math.abs(controlSignal.steer - controlState.steer) < 0.5)
            controlSignal.steer = controlState.steer;
        if (Math.abs(controlSignal.move - controlState.move) < 0.5)
            controlSignal.move = controlState.move;

        if (Math.abs(controlSignal.move) < 20) 
            controlSignal.move = 0;

        drawControlsState({
            left: controlSignal.steer < 0 ? 1 : 0,
            right: controlSignal.steer > 0 ? 1 : 0,
            pwm_steer: 100 * Math.pow(Math.abs(controlSignal.steer) / 100, 2),
            back: controlSignal.move < 0 ? 1 : 0,
            fwd: controlSignal.move > 0 ? 1 : 0,
            pwm_move: 100 * Math.pow(Math.abs(controlSignal.move) / 100, 2)
        });
        if (ws) {
            ws.send(JSON.stringify(controlSignal));
        }
    } else if (ws && Date.now() > lastHeartbeat + 200) {
        lastHeartbeat = Date.now();
        ws.send(heartbeat);
    }
}, 10);


/*
  Touch controls
*/


function initTouch(touch) {
    return {
        identifier: touch.identifier,
        side: touch.clientX < window.innerWidth / 2 ? 'left' : 'right',
        start: [touch.clientX, touch.clientY],
        position: [touch.clientX, touch.clientY]
    };
}

function updateTouch(touchState, touch) {
    touchState.position[0] = touch.clientX;
    touchState.position[1] = touch.clientY;
}

function ongoingTouchIndexById(idToFind) {
    for (var i = 0; i < ongoingTouches.length; i++) {
        var id = ongoingTouches[i].identifier;

        if (id == idToFind) {
            return i;
        }
    }
    return -1;    // not found
}

var ongoingTouches = [];

var moveTouch = null;
var steerTouch = null;

controlCanvas.addEventListener('touchstart', function (evt) {
    evt.preventDefault();
    var touches = evt.changedTouches;
    for (var i = 0; i < touches.length; i++) {
        var ot = initTouch(touches[i]);
        ongoingTouches.push(ot);
        applyTouch(ot);
        console.log("touchstart:" + i + ".");
    }
}, false);

function applyTouch(ot) {
    if (ot.side === 'left') {
        // Use for movement
        var deltaY = ot.position[1] / window.innerHeight - controlTop;
        deltaY /= controlR / 2;
        controlState.move = Math.max(-1, Math.min(1, -deltaY)) * 100;
        controlSignal.move = controlState.move + 0.001;
    } else {
        // Use for steering
        var deltaX = (ot.position[0] - window.innerWidth * (1 - controlMargin)) / window.innerHeight;
        deltaX /= controlR / 2;
        controlState.steer = Math.max(-1, Math.min(1, deltaX)) * 100;
        controlSignal.steer = controlState.steer + 0.001;
    }
}

controlCanvas.addEventListener('touchmove', function (evt) {
    evt.preventDefault();
    var touches = evt.changedTouches;

    for (var i = 0; i < touches.length; i++) {
        var idx = ongoingTouchIndexById(touches[i].identifier);

        if (idx >= 0) {
            updateTouch(ongoingTouches[idx], touches[i]);
            applyTouch(ongoingTouches[idx]);
        } else {
            console.log("can't figure out which touch to continue");
        }
    }
}, false);

var touchEnd = function (evt) {
    evt.preventDefault();
    var touches = evt.changedTouches;

    for (var i = 0; i < touches.length; i++) {
        var idx = ongoingTouchIndexById(touches[i].identifier);

        if (idx >= 0) {
            var ot = ongoingTouches[idx];
            if (ot.side === 'left') {
                // Use for movement
                controlState.move = 0;
                controlSignal.move = 0.001;
            } else {
                // Use for steering
                controlState.steer = 0;
                controlSignal.steer = 0.001;
            }
            ongoingTouches.splice(idx, 1);  // remove it; we're done
        } else {
            console.log("can't figure out which touch to end");
        }
    }
};

controlCanvas.addEventListener('touchend', touchEnd, false);

controlCanvas.addEventListener('touchcancel', touchEnd, false);



/*
  Keyboard controls
*/

window.onkeydown = function (event) {

    if (!keys[event.key]) {
        if (event.key === 'ArrowLeft') {
            controlState.steer -= 100;
        } else if (event.key === 'ArrowRight') {
            controlState.steer += 100;
        }

        if (event.key === 'ArrowUp') {
            controlState.move += 100;
        } else if (event.key === 'ArrowDown') {
            controlState.rear_lights = 100;
            controlState.move -= 100;
        }

        keys[event.key] = true;
    }

    if (event.key === '1') {
        controlState.front_lights = 0;
    } else if (event.key === '2') {
        controlState.front_lights = 20;
    } else if (event.key === '3') {
        controlState.front_lights = 50;
    } else if (event.key === '4') {
        controlState.front_lights = 100;
    } else if (event.key === '0') {
        controlState.rear_lights = controlState.rear_lights ? 0 : 20;
    }

    // console.log(event.key)

    if (event.key === 'z') {
        controlState.blink = -1;
    } else if (event.key === 'c') {
        controlState.blink = 1;
    } else if (event.key === 'x') {
        controlState.blink = 0;
    }

}

window.onkeyup = function (event) {

    if (keys[event.key]) {
        if (event.key === 'ArrowLeft') {
            controlState.steer += 100;
        } else if (event.key === 'ArrowRight') {
            controlState.steer -= 100;
        }

        if (event.key === 'ArrowUp') {
            controlState.move -= 100;
        } else if (event.key === 'ArrowDown') {
            controlState.rear_lights = 20;
            controlState.move += 100;
        }

        keys[event.key] = false;

    }

};


connect();
connectSensors();

function resize() {
    controlCanvas.width = window.innerWidth;
    controlCanvas.height = window.innerHeight;
    drawControlsState(lastControlsState);
}

window.addEventListener('resize', resize, false);

resize();
