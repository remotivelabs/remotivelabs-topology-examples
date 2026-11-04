# ECUs

One folder per ECU, one file per way of running it. A main instance is a list
of these files, so what an ECU is in a topology is one line, and swapping a
model for a mock, an FMU or a recording is changing that line.

| File | The ECU is |
|------|------------|
| `mock.instance.yaml` | a restbus sending every frame of the ECU with default signal values; a test, a dashboard or the command line sets what it sends |
| `broker.instance.yaml` | a bare RemotiveBroker: no model, no restbus; its signals are set and read by hand |
| `python.instance.yaml` | the Python behavioral model in [`models/<ecu>/python`](../../models) |
| `fmu.instance.yaml` | the FMU in [`models/bcm/fmu`](../../models/bcm/fmu), wrapped by a small Python model |
| `playback.instance.yaml` | a model replaying the ECU's part of a recorded drive, see [`android/local_playback.instance.yaml`](../android/local_playback.instance.yaml) |
| `agl_cluster.instance.yaml` | an instrument cluster container on the CAN buses, see [`agl_cluster`](../agl_cluster/README.md) |
| `android_emulator`, `vhal_grpc`, `cuttlefish` | the IHU attached to Android, see [`android`](../android/README.md) |

What each instance uses:

| ECU  | [hello_world](../hello_world/main.instance.yaml) | [fmu](../fmu/main.instance.yaml) | [android](../android/main.instance.yaml) | [agl_cluster](../agl_cluster/main.instance.yaml) |
|------|-------------|--------|----------|-------------|
| ABS  | mock        | mock   | playback | mock        |
| BCM  | python      | fmu    | python   | mock        |
| BMS  | python      | mock   | playback | mock        |
| DIM  | broker      | broker | –        | agl_cluster |
| FLCM | broker      | broker | –        | –           |
| GWM  | python      | python | python   | –           |
| HVAC | broker      | broker | broker   | –           |
| IHU  | python      | python | python, plus android_emulator, vhal_grpc or cuttlefish from the files in [android](../android) | – |
| PAM  | mock        | mock   | –        | –           |
| PCM  | mock        | mock   | playback | –           |
| RL   | python      | python | –        | –           |
| RLCM | python      | python | –        | –           |
| SCCM | mock        | mock   | playback | –           |
| TCU  | mock        | mock   | playback | –           |

An ECU not in an instance is not on the bus. Every file includes the platform,
so any of them can be added to a build on its own, for example the cluster on
top of the Android instance:

```bash
remotive topology build \
-f remotive_car/instances/android/main.instance.yaml \
-f remotive_car/instances/ecus/DIM/agl_cluster.instance.yaml \
remotive_car/build
```

Swapping works the same way: include `SCCM/python` instead of
`SCCM/mock` and a physical steering wheel on the host drives the bus.
