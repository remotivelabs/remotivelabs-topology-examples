# E2E Restbus Example

The purpose of example is to showcase the RemotiveTopology python API using CAN with E2E. The components in this example do not represent realistic automotive components.

The sample shows two ECUs ([EcuA](ecus/ecu_a.py), [EcuB](ecus/ecu_b.py)) which are connected to each other using CAN which travels over UDP. They also communicate on a virtual network.

## Prerequisites to run the example

To execute the example, you need

- **Remotive Topology CLI**
  ➤ [Installation instructions](https://docs.remotivelabs.com/docs/remotive-topology/install)

- **Docker**
  ➤ [Learn more about Docker](https://www.docker.com/)

## Building and Running the Topology

Navigate to the root of this repository (not the folder of the example). Generate the topology and run the example test cases. Make sure that REMOTIVEBROKER_LICENSE is a valid license file in the root of the repository.

```shell
remotive-topology generate -f e2e_restbus/topology/main.instance.yaml build
docker compose -f build/e2e-restbus/docker-compose.yml --profile tester up --build --exit-code-from tester
```

See [RemotiveBroker License](/README.md#remotivebroker-license) for more information about licensing.

This text will describe how the Simple RestBus Sample ties to the key parts in [RemotiveTopology Framework](/README.md).

## Topology Platform

Looking in the [topology.platform.yaml](topology/topology.platform.yaml) file, we see that we are working with a platform with the two ECUs mentioned above and a CAN channel called `Can0`.

## ECU configuration and Topology Instance

Inside the [main.instance.yaml](topology/main.instance.yaml) there is information about how we will simulate the platform. The two ECUs have behavior models written in python. The models can be found in the `ecus`folder.

The CAN channel will be using UDP for transportation, to make it possible to use on Windows and MacOS as well as Linux. (A true CAN environment is only available on Linux.) The network traffic will still be encoded as CAN frames.

### RestBus

[EcuA](ecus/ecu_a.py) demonstrates how to use the simulation context in order to update the signal value of `SomeFrame_10ms.SomeCounter` which RestBus will publish instead of the default value.

[EcuB](ecus/ecu_b.py) demonstrates how to use RestBus in order to update the signal value of `E2eAutosar01A_Ranged.Range_Number` before the value is emitted by RestBus.

**EcuA** sends the virtual message `virtual_frame` to **EcuB** to showcases this feature.

## Extending the Topology

The ECUs in this example are fully virtual, but could also be mixed in the sense that it includes "physical ecus". Current supported protocols are _udp_, _can_, _vcan_ and _lin_. This example used CAN.

### System orchestration and testing

All simulated ECUs can be controlled from code allowing central orchestration, a sample using pytest can be be found [here](test_virtual_interface.py).

## How to get going (mini setup - easier)

This section describes how to get going with a setup that is easy to configure by running different parts of the setup independently with docker.

To create the files used by docker, you need to generate the topology before running any of the commands below. You generate the topology with the Remotive Topology CLI. Remember that you need to run these commands from the root of the repository.

```bash
remotive-topology generate -f e2e_restbus/topology/main.instance.yaml e2e_restbus/build
```

### Start ECUs

From the root of the repository. Start the easy setup by running:

```bash
docker compose -f e2e_restbus/build/e2e-restbus/docker-compose.yml up --build
```

This will start start the ECU simulations and keep them running until you interrupt them with Ctrl-C.

#### Start ECUs in Detached Mode

From the root of the repository. Start the easy setup in detached mode by running:

```bash
docker compose -f e2e_restbus/build/e2e-restbus/docker-compose.yml up --build -d
```

This will keep them running in the background. To stop the simulation, run the "down" command:

```bash
docker compose -f e2e_restbus/build/e2e-restbus/docker-compose.yml down
```

#### Run tests

##### Alternative 1

From the root of the repository. Run the following command to exit with the exit code of the tester

```bash
docker compose -f e2e_restbus/build/e2e-restbus/docker-compose.yml --profile tester up --build --exit-code-from tester
```

This command is suitable for CI as it only requires one command. It will start all ECUs, run the tests and shut everything down when the tests are finished.

##### Alternative 2

From the root of the repository. Run the following command to start the ECUs and keep them running. (You could add the `-d` flag to run them in detached mode.)

```bash
docker compose -f e2e_restbus/build/e2e-restbus/docker-compose.yml up ecu-a ecu-b remotive-broker
```

Then, in a different terminal start just the tests. They will automatically connect to the running ECUs:

```bash
docker compose -f e2e_restbus/build/e2e-restbus/docker-compose.yml --profile tester up tester
```

This command is suitable if you develop tests and don't necessarily want to restart the ECUs.
It also separate the logs of the test from ECU logs.

### Developer Environment

This is helpful if you want to develop your own ECU or play with the examples.

Run the following commands from the root of the repository.

Create a virtualenv and activate it

```shell
python -m venv .venv && source .venv/bin/activate
```

To leave the environment simply run or exit your terminal

```shell
deactivate
```

Install requirements

```shell
cd examples && pip install -r requirements.txt && cd -
```

Using an virtualenv is optional but recommended. Most editors support virtual environments for code completion and inline documentation, for example [vscode](https://code.visualstudio.com/docs/python/environments).

### RemotiveBroker UI

You can start the Remotive Broker UI App, by using the `web-app` docker profile:

```bash
docker compose -f e2e_restbus/build/e2e-restbus/docker-compose.yml --profile web-app up --build
```

Navigate to [http://127.0.0.1:8080/](http://127.0.0.1:8080/) to get a graphical overview of your setup.

Further RemotiveBrokerApp documentation can be found [here](https://docs.remotivelabs.com/docs/remotive-broker/remotive-broker-app).

### Troubleshooting

Sometimes it's necessary to not only restart the containers, but also the entire docker daemon. With a standard Docker installation, in a _systemd_ OS run `service docker restart`.
