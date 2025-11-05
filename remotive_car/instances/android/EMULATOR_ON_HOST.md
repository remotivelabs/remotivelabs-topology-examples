# Android emulator on host
The emulator can also be run on your host while letting the IHU connect to it from within the topology. This can allow for more rapid development of Android applications. The instructions will differ based on which platform you run on, these instructions cover two different configurations:

- Linux with `socketcan` or MacOS/Windows without `socketcan`
- MacOS or Windows combined with a Linux VM which enables `socketcan`

The instructions require running multiple commands on the command line so prepare to have a few terminals ready.

## Setup

To run the emulator on the host it puts some requirements on the android image being used. Use `Android Studio` and create a AVD, make sure it a `userdebug` build which can be started in `permissive` mode. In this demo the AVD is based on `Android Automotive 13 "Tiramisu" with Google APIs ARM 64 v8a System Image`, which comes with `VHAL`. Install a maps apk, eg <https://www.apkmirror.com/apk/google-inc/google-maps-android-automotive/>.

You also need the tool `socat` to be able to redirect ports

```
# Linux
sudo apt install jq socat

# MacOS
brew install jq socat
```

## Linux with socketcan or MacOS/Windows without socketcan

1. In terminal A:
Restart the adb server with `-a` flag that allows listening on all interfaces which allows connections from the topology. Also run it on a different port than standard to avoid conflicts.

    ```
    adb kill-server
    adb -a -P 5038 nodaemon server start
    ```

2. In terminal B:
Redirect tcp ports from 6000 to 5554. The emulator console port is not reachable from within the topology so the connection will be routed through port 6000.

    ```
    socat TCP-LISTEN:6000,fork,reuseaddr TCP:localhost:5554
    ```

3. In terminal C:
Start your android emulator. Adjust the SDK path and emulator name as needed by your installation.

    ```
    ANDROID_ADB_SERVER_PORT=5038 ~/Library/Android/sdk/emulator/emulator @Tiramisu_API_33_automotive -selinux permissive -no-snapshot
    ```

## MacOS or Windows combined with a Linux VM

This examples allows you to run with `socketcan`, despite using a MacOS or Windows computer. It comes with some added complexity of running a Linux VM in which you need to run some commands.

1. Connect to your `linux`

    ```
    ssh user@192.168.64.3 -L 50051:localhost:50051 -L 8080:localhost:8080 -L 8081:localhost:8081 -L 8888:localhost:8888 -L 5001:localhost:5001 -R 5555:localhost:5555 -R 15554:localhost:5554
    ```

    Make sure that the `~/.emulator_console_auth_token` does exits, if you are in a VM you need to copy the file from the host where the emulator is running.

1. In terminal A on `linux`:
Restart the adb server with `-a` flag that allows listening on all interfaces which allows connections from the topology. Also run it on a different port than standard to avoid conflicts.

    ```
    adb kill-server
    adb -a -P 5038 nodaemon server start
    ```

2. In terminal B on `linux`:
Redirect tcp ports from 6000 to 15554. The emulator console port is not reachable from within the topology so the connection will be routed through port 6000.

    ```
    socat TCP-LISTEN:6000,fork,reuseaddr TCP:localhost:15554
    ```

3. In terminal on `host`:
    Start your android emulator

    ```
    ANDROID_ADB_SERVER_PORT=5038 ~/Library/Android/sdk/emulator.backup/emulator @Tiramisu_API_33_automotive -selinux permissive -no-snapshot
    ```

## Hints

- `adb` commands can be run as normal, however `-P 5038` needs to be appended, such as `adb -P 5038 logcat`, alternatively `ANDROID_ADB_SERVER_PORT=5038 adb logcat`
- `run.sh` scripts (above) returns and logs your cloud broker. When you seek you Android location will be updated acordingly.
- wireshark and edgeshark is very useful in this setup <https://docs.remotivelabs.com/docs/remotive-topology/tools/wireshark>

## Troubleshooting

- Make sure that the adb server is running before the emulator is started
- Make sure there is only one one adb server
- Make sure there is only one emulator runnning
- Make sure that Android studio is not running. Read more in Emulator section.
- If the stream stops it probably reached end of drive. Check **Hints** above.

### Emulator

There is no way simple way to start android in `permissive` mode which is required for VHAL and custom properties from Android Studio. If you only need `emu` support and still like to launch from Android Studio, then make sure to change adb port. Located in Debugger options, use port 5038.

> Hint: If you launch from command line, you can still connect your emulator.

### VHAL properties

make sure to **BOOT** in permissive mode

```
ANDROID_ADB_SERVER_PORT=5038 ~/Library/Android/sdk/emulator/emulator @Tiramisu_API_33_automotive -selinux permissive -no-snapshot
```

check vhal

```
adb shell setenforce 0
adb shell getenforce
# Should return: Permissive
adb logcat | grep "Vehicle"
adb shell lsof -iTCP -sTCP:LISTEN
# make sure you see port 33452 or 9342 (this project is set prebuilt fgr 33452)
```

### Useful resources

- <https://developer.android.com/tools/adb>
- <https://twosixtech.com/blog/integrating-docker-and-adb>
- <https://stackoverflow.com/questions/46898322/emulator-5554-unauthorized-for-adb-devices>
