
'use strict';

var remoteVideoElement = document.getElementById("remoteVideo");
var localVideoElement = document.getElementById("localVideo");

var websocketSignalingChannel = 
    new WebSocketSignalingChannel(remoteVideoElement, localVideoElement);




