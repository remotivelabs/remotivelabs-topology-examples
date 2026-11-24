---
id: edgeshark
title: Inspect traffic with Edgeshark
summary: Capture the network traffic of the topology's containers in Wireshark
category: visualize
example: edgeshark_for_podman
domains: []
protocols: [SOME/IP, Ethernet]
key_files:
  - docker-compose-localhost-podman.yaml
related: [ethernet-gateway, android-cuttlefish]
run:
  commands:
    - podman compose -f edgeshark_for_podman/docker-compose-localhost-podman.yaml up
  after: Pick a container network in Edgeshark and capture it in Wireshark.
screenshot:
  kind: manual
---

# Inspect traffic with Edgeshark

[Edgeshark](https://edgeshark.siemens.io/#/) lets you capture the network traffic of containers live in Wireshark,
which is useful to see what actually goes over the virtual networks of a topology, such as SOME/IP services or CAN
frames sent over UDP.

- [Edgeshark for Podman](../edgeshark_for_podman/README.md)
- Compose file: [docker-compose-localhost-podman.yaml](../edgeshark_for_podman/docker-compose-localhost-podman.yaml)

With Docker, use the compose file from the [Edgeshark documentation](https://edgeshark.siemens.io/#/). With Podman, use
the one in this example:

```bash
podman compose -f edgeshark_for_podman/docker-compose-localhost-podman.yaml up
```

Notice:
- The only change from the original file is an explicit hostname for the `gostwire` service. Docker derives it from
  the service and network names, but Podman doesn't.
