# Basic Restbus Example

This example demonstrates how to use RemotiveTopology as a simple way to simulate a restbus.

While RemotiveTopology allows you to spin up full vehicle platforms, it can also be a useful tool if the only thing you need is a simple restbus. By defining a minimal platform with only a single ECU, you can attach it to a CAN bus and use it as a way to stimulate other ECUs. This example instantiates a restbus for a limited SCCM module that is attached to a CAN bus named `DriverCan0`, and allows you to update the signals programmatically. It also shows how you can use recorded data to replay it onto a CAN bus. It works both using a virtual and hardware CAN bus. For a more extensive example, check out [remotive_car](../remotive_car/README.md).

## Prerequisites

- [Docker](https://docs.docker.com/engine/install/)
- [RemotiveTopology CLI](https://docs.remotivelabs.com/docs/remotive-cli) (`remotive`)
- [RemotiveBus](https://docs.remotivelabs.com/docs/remotive-bus)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

## Key Concepts

### Platform

The platform file is where the included databases, communication channels and ECUs are described. In this minimal example there is only one database, one ECU and a single CAN bus channel.

### Instances

The instance file is where it is described how to instantiate the platform. By configuring the ECU to run as a `mock` it will instantiate it as a restbus without any extra logic.

```yaml
ecus:
  SCCM:
    mock: {}
```

### Python

The python folder holds some utility script that can be used to set the values of the restbus. These are sample scripts, intended to show how to programmatically update the values of a restbus using the RemotiveTopology python library.

```python
await broker_client.restbus.update_signals(
    ("SCCM-DriverCAN", [
        RestbusSignalConfig.set(
            name="SteeringAngle.SteeringAngle",
            value=42
        )
    ])
)
```

### Recordings

The recordings can be used to replay an existing candump or csv log of frames/signals. It can optionally include transformations of signals in case recordings come from a different channel/platform than they are replayed on. The example's recording is a minimal version of the larger `remotive_car` example. You can look at the more advanced recording examples in the `remotive_car` example or read more about it in the [documentation](https://docs.remotivelabs.com/docs/remotive-topology/usage/recordings).

## Quick Start

### Programmatically update restbus values

```bash
# Generate the topology configuration
remotive topology generate -f basic_restbus/instances/mock.instance.yaml build/

# Start the restbus
docker compose -f build/basic_restbus_mock/docker-compose.yml --profile ui up --build

# or
cd basic_restbus/python
uv sync
uv run -m update_restbus --signal SCCM-DriverCan0:SteeringAngle.SteeringAngle --value 123.45
```

To see the signals being emitted by the restbus, visit <http://localhost:8080/> and select the `SteeringAngle` frame on the `topology-DriverCan0` namespace.

By adding subscriptions logic to this code, the ECU becomes bi-directional. Find more examples in the [models](../remotive_car/models) folder.

> The restbus does respect CRC and e2e profiles when present in the database along with default values.

### Playback recorded data

Instead of programmatically setting the values for the restbus it is also possible to load data from a recording like a csv or candump. This example includes minimal csv file with a single signal, `SteeringAngle.SteeringAngle`, and a candump with all frames present in the database.

```bash
# Generate the topology configuration
remotive topology generate -f basic_restbus/instances/recording.instance.yaml build/

# Start the restbus
docker compose -f build/basic_restbus_recording/docker-compose.yml --profile ui up --build

# Load the sample recording, set it to repeat and start it (this can also be managed from the web UI)
remotive broker playback open ./recordings/sample_csv.recordingsession.yaml --url http://localhost:50051
remotive broker playback repeat ./recordings/sample_csv.recordingsession.yaml --url http://localhost:50051
remotive broker playback play ./recordings/sample_csv.recordingsession.yaml --url http://localhost:50051
```

## Modifying the example

### Configure to use a physical CAN device

The restbus will connect to a virtual CAN bus by default but in can be configured to use a physical device on the host by including the `hardware.instance.yaml` when generating.

```bash
remotive topology generate \
  -f basic_restbus/instances/mock.instance.yaml \
  -f basic_restbus/instances/hardware.instance.yaml \
  build/
```

An hardware with SocketCAN support can be used out of the box. Once you connect it will show up as follows.

```
$ ip a s
7: can0: <NOARP,UP,LOWER_UP,ECHO> mtu 72 qdisc pfifo_fast state UP group default qlen 1000
    link/can
```

In this example `can0` is used to map to the real hardware as as shown in the [hardware.instance.yaml](instances/hardware.instance.yaml) file.

### Changing database and signals

To use the example with a different database and signals you can change which database is included in the `platform/topology.platform.yaml` file. Also update the channels, ecu names and signals to match the new database.

### Use a different non matching recording with conversions

To use a different recording, add a new recording-session yaml file in the `recordings/` folder that references a different csv file or candump. If the signals needs to be renamed or values modified there needs to be an added step to convert them, see the more advanced example in `remotive_car/instances/android/playback/local` for how it can be done.

## LIN and non SocketCAN compatible devices

RemotiveLabs support custom devices using a plugin architecture. Navigate to the `plugin` section of our [docs](https://docs.remotivelabs.com/). Example plugin for LIN using Kvaser hybrid device can be found [here](https://github.com/remotivelabs/kvaser-remotivebus-plugin).
