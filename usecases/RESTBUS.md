---
id: restbus
title: Restbus
summary: Send every frame of an ECU from its database, and set signal values from Python
category: simulate
example: basic_restbus
domains: [chassis]
protocols: [CAN]
requires: [remotivebus]
key_files:
  - platform/topology.platform.yaml
  - instances/mock.instance.yaml
  - python/update_restbus
related: [replay-can, hardware-can, python-models]
run:
  build: [instances/mock.instance.yaml]
  after: Open RemotiveStudio and select the SteeringAngle frame on the topology-DriverCan0 namespace.
screenshot:
  kind: static
  source: studio
  view: graph
  file: instances/mock.instance.yaml
---

# Restbus

Use RemotiveTopology to create a simple restbus, i.e. automatically send all frames by one or more ECUs.

You don't need a full vehicle platform for this. A minimal platform with one database, one CAN channel and one ECU is
enough to attach to a CAN bus and stimulate other ECUs. Running the ECU as a `mock` instantiates it as a restbus with no
extra logic:

```yaml
ecus:
  SCCM:
    mock: {}
```

- [Restbus example](../basic_restbus/README.md)
- Platform: [topology.platform.yaml](../basic_restbus/platform/topology.platform.yaml)
- Instance file: [mock.instance.yaml](../basic_restbus/instances/mock.instance.yaml)
- Setting signal values from Python: [update_restbus](../basic_restbus/python/update_restbus)

Build and start the restbus, then set a signal from Python:

```bash
remotive topology build -f basic_restbus/instances/mock.instance.yaml build
docker compose -f build/basic_restbus_mock/docker-compose.yml up --build

# in another terminal
cd basic_restbus/python
uv sync
uv run -m update_restbus --signal SCCM-DriverCan0:SteeringAngle.SteeringAngle --value 123.45
```

Notice:
- The restbus respects CRC and E2E profiles when they are present in the database, along with default values.
- By subscribing to frames as well, the ECU becomes bi-directional: a [behavioral model](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/usecases/BEHAVIORAL_MODELS.md).
- The same restbus can [play back a recording](REPLAY_CAN.md) or run on a [physical CAN device](HARDWARE_CAN.md).
