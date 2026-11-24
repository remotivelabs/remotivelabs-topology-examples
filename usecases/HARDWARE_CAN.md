---
id: hardware-can
title: Physical CAN device
summary: Attach a simulated ECU to a real CAN interface on the host
category: integrate
example: basic_restbus
domains: [chassis]
protocols: [CAN]
requires: [remotivebus, can-device]
key_files:
  - instances/hardware.instance.yaml
  - instances/mock.instance.yaml
related: [restbus, replay-can]
run:
  build: [instances/mock.instance.yaml, instances/hardware.instance.yaml]
  after: Check with candump can0 that the restbus frames reach the device.
screenshot:
  kind: static
  source: studio
  view: graph
  file: instances/mock.instance.yaml
---

# Physical CAN device

A topology uses a virtual CAN bus by default. Including one more instance file maps a channel to a CAN device on the
host instead, so the same simulated ECUs talk to real hardware.

- [Restbus example](../basic_restbus/README.md#configure-to-use-a-physical-can-device)
- Instance file that maps `DriverCan0` to `can0`: [hardware.instance.yaml](../basic_restbus/instances/hardware.instance.yaml)

Build the [restbus](RESTBUS.md) with the hardware mapping, and start it:

```bash
remotive topology build \
  -f basic_restbus/instances/mock.instance.yaml \
  -f basic_restbus/instances/hardware.instance.yaml \
  build
docker compose -f build/basic_restbus_mock/docker-compose.yml up --build
```

Notice:
- Any device with SocketCAN support works out of the box. Once connected it shows up as a `can` link in `ip a s`.
- LIN and devices without SocketCAN support use RemotiveBus plugins, for example the
  [Kvaser plugin](https://github.com/remotivelabs/kvaser-remotivebus-plugin).
