#!/bin/bash
# Starts the instrument cluster inside the DIM ECU container: the Qt cluster
# on a VNC framebuffer and noVNC serving it as a web page on port 6080.
set -eu

CAN_CHASSIS="${CAN_CHASSIS:-chassiscan0}"
CAN_BODY="${CAN_BODY:-bodycan0}"

trap 'kill 0' INT TERM

echo "cluster: waiting for CAN interfaces ${CAN_CHASSIS} and ${CAN_BODY}"
until [ -d "/sys/class/net/${CAN_CHASSIS}" ] && [ -d "/sys/class/net/${CAN_BODY}" ]; do sleep 0.5; done

cluster-dashboard &
websockify --web /usr/share/novnc 6080 127.0.0.1:5900 &

# Exit as soon as any of the processes exits so the container restarts cleanly.
wait -n
kill 0
