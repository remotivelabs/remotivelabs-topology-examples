---
id: ethernet-gateway
title: Same tests as the ECU matures
summary: One test for a gateway ECU, whether it is a model, a container or hardware
category: test
example: ethernet_p2p
domains: [gateway]
protocols: [Ethernet]
key_files:
  - platform/network.platform.yaml
  - instances/model.instance.yaml
  - instances/container.instance.yaml
  - instances/external.instance.yaml
  - ecub_model/src/__main__.py
  - ecub_standalone/ecub.py
  - tests/pytest
related: [behavioral-model-test, pytest]
run:
  build: [instances/model.instance.yaml]
  after: In a second terminal, run the tests with cd ethernet_p2p/tests and uv run pytest -s -vv.
screenshot:
  kind: static
  source: studio
  view: graph
  file: instances/model.instance.yaml
---

# Same tests as the ECU matures

An ECU under development usually starts as a model, becomes software in a container and ends up as hardware. With
RemotiveTopology the tests stay the same through all three: only the instance file that says how the ECU runs changes.

In this example `ECUB` is a gateway that forwards frames from `ECUA` on one Ethernet network (`NET1`) to `ECUC` on
another (`NET2`). The test sets signals on `ECUA` and checks that the same values arrive at `ECUC`.

- [Ethernet peer-to-peer example](../ethernet_p2p/README.md)
- Platform with two Ethernet channels: [network.platform.yaml](../ethernet_p2p/platform/network.platform.yaml)
- `ECUB` as a behavioral model: [model.instance.yaml](../ethernet_p2p/instances/model.instance.yaml) and
  [the model](../ethernet_p2p/ecub_model/src/__main__.py)
- `ECUB` as a plain UDP script in a container: [container.instance.yaml](../ethernet_p2p/instances/container.instance.yaml)
- `ECUB` outside Docker, as external hardware would be: [external.instance.yaml](../ethernet_p2p/instances/external.instance.yaml)
  and [ecub.py](../ethernet_p2p/ecub_standalone/ecub.py)
- The tests: [tests/pytest](../ethernet_p2p/tests/pytest)

Build and start the model variant, then run the tests in a second terminal:

```bash
remotive topology build -f ethernet_p2p/instances/model.instance.yaml build
docker compose -f build/ethernet-p2p-model/docker-compose.yml up --build

# in another terminal
cd ethernet_p2p/tests
uv run pytest -s -vv
```

Notice:
- Swap `model` for `container` or `external` in both commands to test the other variants. The external variant also
  needs host network setup, see the [example README](../ethernet_p2p/README.md).
- The test only talks to `ECUA` and `ECUC`, which is why it doesn't change when `ECUB` does.
