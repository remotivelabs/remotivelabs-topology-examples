# RemotiveLabs and Android Emulator

This is a set of Python scripts to redirect data from [RemotiveCloud](https://cloud.remotivelabs.com/) to AAOS emulator.

![Example](docs/source/example.gif)

Check the [video](media/video_example_location_broker_to_emu_720.mov) in */media* for an example on how location can be sent from [RemotiveCloud](https://cloud.remotivelabs.com/)
to AAOS emulator.

## Setup

It is highly recommended that you read the documentation in *docs/build/html/index.html*,
as it describes the steps in more details. It can be tricky to make it work if you miss
some configurations.

Make sure to install the dependencies.

```bash
pip install -r requirements.txt
```

Download the Android Studio Preview version:
https://developer.android.com/studio/preview

## Run

Create a free [RemotiveCloud](https://cloud.remotivelabs.com/) account and go to the Recordings page. Choose the _City drive to Turning Torso_ recording and start the playback. Make sure to pick _configuration_android_ when playing. 
**Note!** If you already have an account, you can import the _City drive to Turning Torso_ recording by clicking the import icon in the upper right corner of the recording page. 

### Send Location

Run the [AAOS Emulator](https://developer.android.com/studio/run/managing-avds).
For sending location, you can use an user image such as:
* Automotive 12L with Play Store ARM 64 v8a System Image
    * If your machine is **ARM** based. It is an user build with GAS.
* Automotive 12L with Play Store Intel x86 Atom_64 System Image
    * If your machine is **x86** based. It is an user build with GAS.


Include the credentials from the broker (URL and API key) as well as the LATITUDE and LONGITUDE signals:
```bash
$ python3 br_location_to_emu.py --url $URL --x_api_key $KEY --namespace android --signal LATITUDE --signal LONGITUDE
```
**Note!** You can find the broker credentials in the bottom left corner once you have prepared the recording for playback.

### Set VHAL Properties
To manipulate VHAL properties, you must use an userdebug build:
* Android Automotive 13 "Tiramisu" with Google APIs ARM 64 v8a System Image
    * It does not contain GAS, but it is userdebug.

Run the emulator via [command line](https://developer.android.com/studio/run/emulator-commandline):
```bash
$ emulator @$avd_name -selinux permissive -no-snapshot
```
Note that you must set SELinux as permissive mode.

If you want to send VHAL property values to AAOS emulator:
```bash
$ python3 br_props_to_aaos.py --url $URL --x_api_key $KEY --namespace android --signal $SIGNAL
```
alternatively
```bash
$ PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python python3 br_props_to_aaos.py --url $URL --x_api_key $KEY --namespace android --signal $SIGNAL
```
Send the signals you want by always putting the flag *--signal* alongside its name.

## Documentation
Check docs/build/html/index.html for further details regarding this project, including how to setup
your environment, emulator and scripts. 

There is also a section about lessons learned and improvements for this project (docs/build/html/insights.html).

# RemotiveLabs and Cuttlefish virtual Android devices
In this setup you can get Android running in a containerized environment

## Setup cuttlefish

![Example](media/video_example_location_broket_to_cuttlefish.gif)

Check the [video](media/video_example_location_broket_to_cuttlefish.mov) in */media* for an example on how location can be sent from [RemotiveCloud](https://cloud.remotivelabs.com/)

### Setup your cuttlefish deployment

- Follow this guide: https://source.android.com/docs/devices/cuttlefish/get-started
- Navigate to your cuttlefish deployment eg https://localhost:8443/

In the screenshots `https://organicmaps.app/` is used, download the apk and install it by doing `adb install app.organicmaps_25030207.apk`

## Start playback of you desired stream

> Below hints are copied from the graphical playback interface.
```
remotive cloud auth login
remotive cloud recordings mount 13303517729834103000 --transformation-name 'configuration_android'  --project aleks-base-on-open
remotive cloud recordings seek 13303517729834103000 --seconds 60 --project aleks-base-on-open
remotive cloud recordings play 13303517729834103000 --project aleks-base-on-open
```

# Subscribe to the cloud stream and send the location to Cuttlefish virtual Android device (cvd-1)
```
$ python3 br_location_to_cuttlefish.py --url $URL --x_api_key $KEY --namespace android --signal LATITUDE --signal LONGITUDE -cvd_url https://localhost:1443/devices/cvd-1
```

### Useful hints

If you are deploying in cloud this port config might be handy. It enables `WebRTC` along with `ADB` and a `rest` interface.  
```
ssh -i ~/.ssh/google_compute_engine aleksandar_remotivelabs_com@34.34.135.209 -L 8443:localhost:8443 -L 5555:localhost:5555 -L 15550:localhost:15550 -L 15551:localhost:15551 -L 15552:localhost:15552 -L 15553:localhost:15553 -L 15554:localhost:15554 -L 15555:localhost:15555 -L 15556:localhost:15556 -L 15557:localhost:15557 -L 15558:localhost:15558 -L 15559:localhost:15559 -L 5037:localhost:5037 -L 1443:localhost:1443
```

The coordinates are sent using `rest` to the Cuttlefish virtual Android device, more information can be found here: https://source.android.com/docs/devices/cuttlefish/control-environment. 

Protos for location can be found here: https://android.googlesource.com/device/google/cuttlefish/+/refs/heads/master/host/commands/gnss_grpc_proxy/gnss_grpc_proxy.proto

# Android ADB and EMULATOR - how to get going

## Prerequisites

install 
- RemotiveCLI https://docs.remotivelabs.com/docs/remotive-cli/installation
- RemotieToplogy https://docs.remotivelabs.com/docs/remotive-topology/install
```
# linux
sudo apt install jq socat
```
```
# MacOS
brew install jq socat
```

1.
    1. Start your android emulator
    ```
    ~/Library/Android/sdk/emulator.backup/emulator @Tiramisu_API_33_automotive -selinux permissive -no-snapshot
    ```
    > Android Automotive 13 "Tiramisu" with Google APIs ARM 64 v8a System Image, comes with VHAL. 
    
    2. Install Maps or similar, `adb install path_to_apk`. Eg https://www.apkmirror.com/apk/google-inc/google-maps-android-automotive/
    this will start a ADB server make sure to remove it again `adb kill-server`
    

2. Only for MacOS users who need socketcan

    `ssh aleksandar@192.168.64.3 -L 50051:localhost:50051 -L 8080:localhost:8080 -L 8081:localhost:8081 -L 8888:localhost:8888 -L 5001:localhost:5001 -L 5038:localhost:5038 -R 5555:localhost:5555 -R 15554:localhost:5554`

**If** step 2 was executed the following should be started in that ssh host

3. start `adb -a -P 5038 nodaemon server start`  

4. 
    1. set up port redirection (adb only accepts connections from localhost)
(with ssh). `socat TCP-LISTEN:5554,fork,reuseaddr TCP:localhost:15554` (apt install socat)
    
    2. (alternatively without ssh). `socat TCP-LISTEN:5554,fork,reuseaddr TCP:localhost:5554` (apt install socat, brew install socat)

5. Generate topology

Unless already signed in start by doing `remotive cloud auth login`

# Linux
```
remotive-topology generate \
  -f lighting_and_steering/topology/main.instance.yaml \
  -f lighting_and_steering/topology/android.instance.yaml \
  lighting_and_steering/build
```
# MacOS and Windows
```
remotive-topology generate \
  -f lighting_and_steering/topology/main.instance.yaml \
  -f lighting_and_steering/topology/android.instance.yaml \
  -f lighting_and_steering/topology/can_over_udp.instance.yaml \
  lighting_and_steering/build
```


6. Start the topology docker compose up
```
export CLOUD_URL=$(./run.sh)
CLOUD_AUTH=$(remotive cloud auth print-access-token) \
ANDROID_EMULATOR_AUTH=$(cat ~/.emulator_console_auth_token) \
docker compose -f lighting_and_steering/build/lighting-and-steering/docker-compose.yml --profile jupyter --profile ui up
```
> make sure that the `~/.emulator_console_auth_token` does exits, if you are in a VM you need to copy the file from the host where the emulator is running.


### Android

Make sure to only have **one** instance of android running.

#### Emulator
There is no way simple way to start android in `permissive` mode which is required for VHAL and custom properties. If you only need `emu` support and still like to launch from Android Studio, then make sure to change adb port. Located in Debugger options, use port 5038.

> Hint: If you launch from command line, you can still connect your emulator.

#### VHAL properties
make sure to BOOT in permissive mode
```
~/Library/Android/sdk/emulator.backup/emulator @SmallAutoAPI33 -selinux permissive -no-snapshot
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
- https://developer.android.com/tools/adb
- https://twosixtech.com/blog/integrating-docker-and-adb/?utm_source=chatgpt.com
- https://stackoverflow.com/questions/46898322/emulator-5554-unauthorized-for-adb-devices
