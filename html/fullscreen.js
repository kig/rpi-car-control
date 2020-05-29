var fullscreenButton = document.getElementById('fullscreen');
if (fullscreenButton && (document.exitFullscreen||document.webkitExitFullscreen||document.webkitExitFullScreen||document.mozCancelFullScreen||document.msExitFullscreen)) {
    fullscreenButton.onclick = function() {
	var d = document;
	if (d.fullscreenElement||d.webkitFullscreenElement||d.webkitFullScreenElement||d.mozFullScreenElement||d.msFullscreenElement) {
	    (d.exitFullscreen||d.webkitExitFullscreen||d.webkitExitFullScreen||d.mozCancelFullScreen||d.msExitFullscreen).call(d);
	} else {
	    var e = document.body;
	    (e.requestFullscreen||e.webkitRequestFullscreen||e.webkitRequestFullScreen||e.mozRequestFullScreen||e.msRequestFullscreen).call(e);
	}
    }
    if (window.navigator.standalone === true) {
	fullscreenButton.style.opacity = '0';
    }
} else if (fullscreenButton) {
    fullscreenButton.style.opacity = '0';
}
