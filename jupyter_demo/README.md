# Jupyter advanced examples

This example shows how to mock ECUs using jupyter, both programmatically and using a simple UI. This example also includes how to use candump/cansend and similar command line tools for UDP

The goal is to have a very simple setup using standard tools that should be easy to setup with minimal dependencies.

## Demo setup

There are two ways to run the RemotiveBroker for this demo:

- UDP (easy docker setup provided)
- VCAN (Linux required)

The mocking code is identical as the RemotiveBroker abstracts the protocol differences.

### Option A: Using UDP

Simply start the RemotiveBroker with UDP configuration:

```sh
docker compose -f ./docker-compose-broker.yml up
```

Open two terminal windows for sending and receiving data.

Receive:

```sh
docker compose -f ./docker-compose-udptools.yml up
```

Send: MyFrame.MySignal (00a) with a value of 0x42:

```sh
docker exec -it jupyter_demo-udptools-1 /bin/bash
TARGET_HOST=remotive-broker TARGET_PORT=5001 python3 send.py 00a#0042
```

### Option B: Using VCAN

This is a more real setup and can easily be changed to can interface.

Start a broker in using a `RemotiveBox` or prepare your custom setup using `https://github.com/remotivelabs/remotivebroker-bootstrap`.
Upload the `configuration_vcan`. The `broker_vcan.ipynb` can be used to set the configuration using script.

Open two terminal windows for sending and receiving data.

Receive:

```sh
candump -cex any
```

Send: For example MyFrame.MySignal (00a) with a value of 42:

```sh
cansend vcan0 00a#0042
```

> The same thing can be done using a physical `CAN` bus, but for simplicity reasons this sample used virtual `VCAN`.

## Running jupyter

Start jupyter lab with RemotiveBroker running in Docker:

```sh
REMOTIVE_BROKER_URL=http://remotive-broker:50051 docker compose -f ./docker-compose-jupyter.yml up
```

> `remotive-broker` needs to resolve to the proper ip of you machine where your broker is running. You could also type it explicitly.

Browse to http://127.0.0.1:8888/lab?token=remotivelabs
