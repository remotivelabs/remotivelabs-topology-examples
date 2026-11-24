---
id: raw-playback
title: Raw playback with video
summary: Replay a recorded Tesla Model 3 drive, with its camera videos, onto its CAN buses
category: replay
example: tesla
domains: [chassis, powertrain]
protocols: [CAN]
requires: [git-lfs]
key_files:
  - roundabout/roundabout.recordingsession.yaml
  - platform/tesla.platform.yaml
  - settings/can_over_udp.settings.instance.yaml
related: [signal-playback, replay-can]
run:
  commands:
    - |-
      mkdir tesla/build
      remotive topology recording-session instantiate tesla/roundabout/roundabout.recordingsession.yaml tesla/build/roundabout.instance.yaml
    - |-
      remotive topology build \
        -f tesla/build/roundabout.instance.yaml \
        -f tesla/settings/can_over_udp.settings.instance.yaml \
        tesla/build
    - docker compose -f tesla/build/Roundabout/docker-compose.yml up --build
  after: Open RemotiveStudio and start playback of roundabout.recordingsession.yaml.
screenshot:
  kind: manual
---

# Raw playback with video

Using playback of raw recordings can be useful when testing user interfaces, e.g. using Android or something like
ProtoPie. The recorded data gives you the same frames as you would get sitting in the running vehicle.

This example plays back a recording of a Tesla Model 3 driving through a roundabout: the raw CAN logs of its chassis
and vehicle buses together with the videos from four cameras.

- [Tesla example](../tesla/README.md)
- Recording session: [roundabout.recordingsession.yaml](../tesla/roundabout/roundabout.recordingsession.yaml)
- Platform: [tesla.platform.yaml](../tesla/platform/tesla.platform.yaml)

The topology is generated from the recording session, then built and started:

```bash
mkdir tesla/build
remotive topology recording-session instantiate tesla/roundabout/roundabout.recordingsession.yaml tesla/build/roundabout.instance.yaml
remotive topology build -f tesla/build/roundabout.instance.yaml -f tesla/settings/can_over_udp.settings.instance.yaml tesla/build
docker compose -f tesla/build/Roundabout/docker-compose.yml up --build
```

Use [RemotiveStudio](https://developer.remotivelabs.com/docs/remotive-studio) to view signals and start playback of
`roundabout.recordingsession.yaml`.

Notice:
- The recordings and videos are stored with Git LFS. Run `git lfs pull` if `git lfs` wasn't installed when you cloned.
- There are more sample recordings in [RemotiveCloud](https://cloud.remotivelabs.com/).
