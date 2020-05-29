(function () {
    var ws = null;
    var lastAlive = 0;

    var connect = function () {
        ws = new WebSocket(document.location.toString().replace(/^http/, 'ws') + "video-in");
        ws.binaryType = 'arraybuffer';

        ws.onopen = function (event) {
        };

        ws.onclose = function (event) {
            console.log('Socket is closed. Reconnect will be attempted in 1 second.', event.reason);
            ws = null;
            setTimeout(function () {
                connect();
            }, 1000);
        };

        ws.onerror = function (event) {
            ws.close();
        };

        ws.onmessage = function () {
            lastAlive = Date.now();
        };

    };

    var channels = 1;
    var sampleRate = 44100;
    var kbps = 128;
    var mp3encoder = new Mp3Encoder(channels, sampleRate, kbps);

    var BUFF_SIZE = 2048;

    var samples = new Int16Array(BUFF_SIZE);
    var sampleBlockSize = 576;

    var audioContext = new AudioContext();

    console.log("Audio is starting up ...");

    var audioInput = null,
        microphone_stream = null,
        gain_node = null,
        script_processor_node = null,
        script_processor_fft_node = null,
        analyserNode = null;

    if (!navigator.getUserMedia)
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia || navigator.msGetUserMedia;

    if (navigator.getUserMedia) {

        navigator.getUserMedia(
            {
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            },
            function (stream) {
                start_microphone(stream);
            },
            function (e) {
                console.log('Error capturing audio.', e);
            }
        );

    } else {
        console.log('getUserMedia not supported in this browser.');
    }

    // ---

    function process_microphone_buffer(event) {
        mp3encode(event.inputBuffer.getChannelData(0));
    }

    function start_microphone(stream) {
        console.log('mic started');

        gain_node = audioContext.createGain();
        gain_node.connect(audioContext.destination);

        microphone_stream = audioContext.createMediaStreamSource(stream);

        script_processor_node = audioContext.createScriptProcessor(BUFF_SIZE, 1, 1);
        script_processor_node.onaudioprocess = process_microphone_buffer;

        microphone_stream.connect(script_processor_node);
        script_processor_node.connect(audioContext.destination);

    }

    var sampleI16 = new Int16Array(BUFF_SIZE);
    function mp3encode(sample) {
        if (ws && ws.readyState === 1 && Date.now() - lastAlive < 3000) {
            /* Send raw data

            for (var j = 0; j < sample.length; j++) {
                sampleI16[j] = sample[j] * 10 * 0x7FF;
            }
            ws.send(sampleI16);
            */

            /* MP3 encode */
            for (var j = 0; j < sample.length; j += sampleBlockSize) {
                var sampleBlock = sample.slice(j, j + sampleBlockSize);
                var sampleI16 = new Int16Array(sampleBlock.length);
                for (var i = 0; i < sampleBlock.length; i++) {
                    sampleI16[i] = sampleBlock[i] * 10 * 0x7FF;
                }
                var mp3 = mp3encoder.encodeBuffer(sampleI16);
                if (mp3.length > 0) {
                    //console.log(mp3.length);
                    ws.send(mp3);
                }
            }
        }
    }

    connect();

})();
