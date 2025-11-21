# Tesla example
This example shows how to instantiate a topology that can playback recordings from a Tesla Model 3.

There are more sample recordings available from https://cloud.remotivelabs.com/

## Prerequisites
- You will need to install `RemotiveToplogy`, follow the instructions here <https://docs.remotivelabs.com/docs/remotive-topology/install>
- Make sure to `git lfs pull` if `git lfs` wasn't installed during `git clone`, see https://git-lfs.com/

## Getting started

Generate the instance
```bash
mkdir tesla/build
remotive-topology recording-session instantiate tesla/roundabout/roundabout.recordingsession.yaml tesla/build/roundabout.instance.yaml
remotive-topology generate -f tesla/build/roundabout.instance.yaml -f tesla/can_over_udp.instance.yaml tesla/build
```

Start it
```bash
docker compose -f tesla/build/Roundabout/docker-compose.yml --profile ui up --build
```

Browse to [http://localhost:8080](http://localhost:8080) and start playback of `roundabout.recordingsession.yaml`.

## Credits

The DBC files are originally from https://github.com/joshwardell/model3dbc