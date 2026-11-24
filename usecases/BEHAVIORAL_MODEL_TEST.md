---
id: behavioral-model-test
title: Behavioral model and test
summary: A BCM model and a test of the hazard lights, explained step by step
category: start
example: getting_started
domains: [lighting]
protocols: [CAN]
key_files:
  - platform/topology.platform.yaml
  - models/bcm/__main__.py
  - models/bcm.instance.yaml
  - tests/test_hazard_light.py
  - tests/tester.instance.yaml
  - instances/main.instance.yaml
related: [first-topology, pytest, python-models]
run:
  build: [instances/main.instance.yaml, settings/can_over_udp.settings.instance.yaml]
  profiles: [tester]
  up_args: [--abort-on-container-exit]
  after: The tester container runs the test and exits; run the command again to rerun it.
screenshot:
  kind: static
  source: studio
  view: graph
  file: instances/main.instance.yaml
---

# Behavioral model and test

The hello world of RemotiveTopology: describe a small platform, write a behavioral model for one ECU, and test it.

The test checks that the front light control module (`FLCM`) gets the right signal when the hazard lights button is
pressed. The button makes the steering column module (`SCCM`) send a message to the body control module (`BCM`),
whose behavioral model forwards it to the light control modules.

- [Getting started example](../getting_started/README.md), which explains every file
- Platform: [topology.platform.yaml](../getting_started/platform/topology.platform.yaml)
- Behavioral model of the `BCM`: [models/bcm](../getting_started/models/bcm/__main__.py) and its
  [instance file](../getting_started/models/bcm.instance.yaml)
- Test case: [test_hazard_light.py](../getting_started/tests/test_hazard_light.py), run by
  [tester.instance.yaml](../getting_started/tests/tester.instance.yaml)

Build and run the test:

```bash
remotive topology build \
  -f getting_started/instances/main.instance.yaml \
  -f getting_started/settings/can_over_udp.settings.instance.yaml \
  build
docker compose -f build/getting-started/docker-compose.yml --profile tester up --abort-on-container-exit --build
```

Notice:
- The test controls the `SCCM` mock to simulate the button and checks what `FLCM` receives, so it tests the `BCM`
  model through the bus only.
- The same test can run against real ECU software or hardware by replacing the `bcm` instance.
