---
id: replay-can
title: Replay candump or CSV
summary: Play a candump or CSV recording onto a CAN bus
category: replay
example: basic_restbus
domains: [chassis]
protocols: [CAN]
requires: [remotivebus]
key_files:
  - instances/recording.instance.yaml
  - recordings/sample_csv.recordingsession.yaml
  - recordings/sample_candump.recordingsession.yaml
  - recordings/log.csv
  - recordings/candump.log
related: [restbus, signal-playback, raw-playback]
run:
  build: [instances/recording.instance.yaml]
  after: Open and play recordings/sample_csv.recordingsession.yaml in RemotiveStudio, or with remotive broker playback as the example README shows.
screenshot:
  kind: static
  source: studio
  view: graph
  file: instances/recording.instance.yaml
---

# Replay candump or CSV

Instead of setting the values of a [restbus](RESTBUS.md) programmatically, you can load them from a recording, such as
a CSV file of signals or a candump of raw frames, and replay it onto the CAN bus.

- [Restbus example](../basic_restbus/README.md#playback-recorded-data)
- Instance file: [recording.instance.yaml](../basic_restbus/instances/recording.instance.yaml)
- Recording sessions: [sample_csv.recordingsession.yaml](../basic_restbus/recordings/sample_csv.recordingsession.yaml)
  (a single signal, `SteeringAngle.SteeringAngle`) and
  [sample_candump.recordingsession.yaml](../basic_restbus/recordings/sample_candump.recordingsession.yaml) (all frames in
  the database)

Build and start it:

```bash
remotive topology build -f basic_restbus/instances/recording.instance.yaml build
docker compose -f build/basic_restbus_recording/docker-compose.yml up --build
```

Then open the recording session, set it to repeat and play it from [RemotiveStudio](https://developer.remotivelabs.com/docs/remotive-studio)
or with `remotive broker playback`, as the [example README](../basic_restbus/README.md#playback-recorded-data) shows.

Notice:
- A recording session can transform signals, for when the recording comes from a different channel or platform than
  the one it is replayed on. [Signal playback](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/usecases/PLAYBACK_SIGNALS.md)
  in RemotiveCar shows a larger example.
- Read more about recordings in the [documentation](https://developer.remotivelabs.com/docs/remotive-topology/usage/recordings).
