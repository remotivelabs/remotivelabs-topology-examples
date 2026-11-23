# Playback signals

Using playback of recorded data can be useful to test longer scenarios. This example show how recorded [VSS](https://covesa.github.io/vehicle_signal_specification/) signals can be fed into behavioral models that convert them into platform specific signals. In this case the signals include location, steering wheel angle, and pedal positions among others.

- Part of the [RemotiveCar example](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/DOCS.md)
- Instance file: [local_playback.instance.yaml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/instances/android/local_playback.instance.yaml)
- Platform adding VSS channel: [topology.platform.yaml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/recordings/platform/topology.platform.yaml)
- Starting playback: [playback.local](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/instances/android/playback/local/__main__.py)
- Behavioral models converting VSS to RemotiveCar platform: [abs](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/instances/android/playback/local/abs.py), [sccm](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/instances/android/playback/local/sccm.py), [tcu](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/instances/android/playback/local/tcu.py)

Notice:
- In this example playback happens to be part of the Android instance, but playback is not limited to Android use cases. 
- Playback is not limited to VSS. You can also add custom signals or even raw data. 
- This example use CSV, but playback also support other formats, for example candump for raw CAN data. 

To run playback with signals, see [Cuttlefish](./ANDROID_CUTTLEFISH.md) or [Android Emulator](./ANDROID_EMULATOR.md).
