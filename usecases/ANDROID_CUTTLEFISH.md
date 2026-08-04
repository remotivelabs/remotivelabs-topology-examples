# Android Cuttlefish

Using [Cuttlefish](https://source.android.com/docs/devices/cuttlefish) is useful when you are developing applications for your custom Android build or when customizing the Android build. Cuttlefish only works on Linux. 

- Part of the [RemotiveCar example](../remotive_car/DOCS.md) 
- Instance file: [cuttlefish.instance.yaml](../remotive_car/instances/android/cuttlefish.instance.yaml)
- Docker compose overlay: [cuttlefish.compose.yaml](../remotive_car/instances/android/cuttlefish.compose.yaml)
- Convert signals to VHAL properties: [IHU](../remotive_car/models/ihu/python/ihu/__main__.py)
- Review the shared android documentation: [README.md](../remotive_car/instances/android/README.md)

## With Cuttlefish within Docker

The example is pre-configured with a Cuttlefish docker image that works with the topology. This image contains the reference Cuttlefish build for Android Automotive (Android 15). This does not contain any map application and since it does not contain Google Play APIs it will not work to install Google Maps manually. Instead pick another map application of your choice, for example <https://organicmaps.app/>. Place any APK you wish to install in `remotive_car/instances/android/cuttlefish/apks/` and it will be installed when the container starts.

### Build

From the root of this repository run, one of the commands below, depending on your setup.

```bash
# With RemotiveBus
remotive topology build \
-f remotive_car/instances/android/main.instance.yaml \
-f remotive_car/instances/android/cuttlefish.instance.yaml \
remotive_car/build
```

```bash
# Without Remotivebus
remotive topology build \
-f remotive_car/instances/android/main.instance.yaml \
-f remotive_car/instances/android/cuttlefish.instance.yaml \
-f remotive_car/settings/can_over_udp.settings.instance.yaml \
-f remotive_car/settings/vlan_using_bridge.settings.instance.yaml \
remotive_car/build
```

RemotiveTopology uses Docker compose to define the containers and networks of the topology. Once generated, by following the steps in this section, it can be found [here](../../build/remotive_car_android/docker-compose.yml)

### Run

From the root of this repository run

```bash
docker compose -f remotive_car/build/remotive_car_android/docker-compose.yml \
-f remotive_car/instances/android/cuttlefish.compose.yaml \
--profile playback up --build
```

You should then be able to reach the Cuttlefish instance by going to <https://localhost:8443>. The first time it starts you will have to configure some settings and permission for the maps application. If using the Organic Map you will also have to download maps for the areas you are interested in.

If you wish to completely reset the state of the cuttlefish container, remove everything in the `cuttlefish/state` folder except the .gitignore.

Use [RemotiveStudio](https://docs.remotivelabs.com/docs/remotive-studio) to view signals and observe the temperature signals being sent back from the Cuttlefish instance.

### Tests

The Cuttlefish instance provides two tests located in `remotive_car/tests/pytest/android`. These will verify that location updates can flow from the TCU into Android and that HVAC changes in Android will flow back to the TCU. These can be run by running with the `tester` profile (and excluding the `playback` profile).

```bash
docker compose -f remotive_car/build/remotive_car_android/docker-compose.yml \
-f remotive_car/instances/android/cuttlefish.compose.yaml \
--profile tester up --build --abort-on-container-exit
```

The tests can also be run manually if you navigate to `remotive_car/tests/pytest` and run `uv run pytest -m android`.

## With VLAN networking

By default, the remotive command generates normal docker bridge networks to represent the ethernet channels. If the platform specifies special VLAN ids for the channels (see SOMEIP channel) you may want the network traffic to also be tagged, especially if it should be connected to a physical network. You can do this by using the `remotivebus` driver for the ethernet channel. In this example it is done by including the file `vlan_networking.instance.yaml` when generating the topology.

```bash
remotive topology build \
-f remotive_car/instances/android/main.instance.yaml \
-f remotive_car/instances/android/cuttlefish.instance.yaml \
-f remotive_car/instance/vlan_networking.instance.yaml \
remotive_car/build
```

## Notice
- Normally your Android build should include the VHAL property integration with your platform. However, in this example the integration is done using a behavioral model instead, but this is only because we don't have a custom version of Android.

## Troubleshoot
- Maps application is missing in Android Cuttlefish: Make sure to download the APK and put in the folder as described [above](#with-cuttlefish-within-docker).
