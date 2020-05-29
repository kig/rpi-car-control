if ! ps x | grep -v grep | grep -q dbus-daemon
then
	dbus-daemon --session --fork
fi
