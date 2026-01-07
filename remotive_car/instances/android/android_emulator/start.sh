#!/usr/bin/env bash

set -euo pipefail

# Defaults if not provided
: "${DISPLAY:=:0}"
: "${SCREEN_RES:=1920x1080x24}"
: "${NOVNC_PORT:=8080}"
: "${VNC_PORT:=5900}"
: "${EMU_CONSOLE_PORT:=5554}"
: "${EMU_HTTP_FORWARD:=6000}"

# Start a virtual framebuffer X server
if ! pgrep -x Xvfb >/dev/null 2>&1; then
  rm -f /tmp/.X0-lock
  Xvfb "${DISPLAY}" -screen 0 "${SCREEN_RES}" -ac +extension GLX +render -noreset &
  sleep 0.5
fi

# Start a minimal window manager
if ! pgrep -x fluxbox >/dev/null 2>&1; then
  fluxbox >/tmp/fluxbox.log 2>&1 &
  sleep 0.5
fi

# Start VNC server against the existing X display
if ! pgrep -x x11vnc >/dev/null 2>&1; then
  x11vnc \
    -display "${DISPLAY}" \
    -rfbport "${VNC_PORT}" \
    -forever -shared -nopw -repeat -noxdamage \
    -cursor arrow \
    -o /tmp/x11vnc.log &
  sleep 0.5
fi

# Start noVNC server to expose VNC over HTTP
if ! pgrep -f "websockify.*8080" >/dev/null 2>&1; then
  websockify --web "/usr/share/novnc" 0.0.0.0:${NOVNC_PORT} localhost:${VNC_PORT} \
    >/tmp/novnc.log 2>&1 &
fi

echo "${ANDROID_EMULATOR_AUTH}" >~/.emulator_console_auth_token

# Redirect port 6000 to emulator console port 5554 as it can't be exposed directly
socat TCP-LISTEN:${EMU_HTTP_FORWARD},fork,reuseaddr TCP:localhost:${EMU_CONSOLE_PORT} &

EMULATOR_CMD="/opt/android/emulator/emulator -avd android-automotive -selinux permissive -no-boot-anim -gpu off"
echo "Launching emulator: ${EMULATOR_CMD}"
if ! pgrep -f "$EMULATOR_CMD" >/dev/null 2>&1; then
  # Remove any lock files from previous container starts
  rm -f /root/.android/avd/android-automotive.avd/*.lock
  DISPLAY="${DISPLAY}" bash -lc "$EMULATOR_CMD &" >/tmp/emulator.log 2>&1
fi

# Wait for device to be visible
adb wait-for-device

# Wait for full boot completion
echo "Waiting for Android to finish booting..."
until adb shell getprop sys.boot_completed | grep -q "1"; do sleep 1; done

# Install google maps APK
adb install /com.google.android.apps.maps.apk

# Auto launch Maps app (not automatic after install)
adb shell am start -a android.intent.action.MAIN \
  -c android.intent.category.LAUNCHER \
  -n com.google.android.apps.maps/com.google.android.maps.MapsActivity

# Allow apps to be used while driving
adb shell su shell cmd car_service enable-uxr false

# Restart ADB server with -a flag to allow remote connections
adb kill-server && adb -a server start

wait -n
