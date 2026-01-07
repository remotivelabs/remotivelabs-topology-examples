# RemotiveCar example
By following the steps below, you will generate and run an instance of a topology containing multiple communication protocols and multiple ECUs.

## Prerequisites
You will need to install `RemotiveTopology`, follow the instructions here <https://docs.remotivelabs.com/docs/remotive-topology/install>

## Getting started
Generate the instance
```bash
remotive topology generate -f remotive_car/instances/hello_world/main.instance.yaml -f remotive_car/instances/can_over_udp.instance.yaml remotive_car/build
```

Start it
```bash
docker compose -f remotive_car/build/remotive_car_hello_world/docker-compose.yml --profile jupyter --profile ui up --build
```

Browse to [http://localhost:8080](http://localhost:8080) and select the signals you like to monitor.

Browse to [http://localhost:8888/lab?token=remotivelabs](http://localhost:8888/lab?token=remotivelabs) to interact with the instance through a Jupyter notebook.

## Documentation
Further documentation can be found [here](DOCS.md).
