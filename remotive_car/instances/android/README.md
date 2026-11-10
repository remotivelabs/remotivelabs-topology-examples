# Android instance

![Example](docs/RemotiveTopology_ans_AAOS.gif)

This demo shows bidirectional communication with Android. The goal is for you to be be able to follow a recorded drive through Android and observe the location and speed. You can also adjust the temperature in the Android UI and see that the signals are passed back into the topology.

- IHU connected over SOME/IP running Android with live location source

Notice while the example is showing ECUs possible present in a real vehicle, the signals and implementations are simplified to make the example easy to understand. The goal is not intended to be fully realistic.

## Instance overview

[main.instance.yaml](main.instance.yaml) describes the instance as shown in the diagram below.

```mermaid
---
config:
  class:
    hideEmptyMembersBox: true
---
    classDiagram
    namespace ABS {
        class Behavioral_Model_ABS
        class RemotiveBroker_ABS
    }

    namespace BCM {
        class Behavioral_Model_BCM
        class RemotiveBroker_BCM
    }

    namespace HVAC {
        class RemotiveBroker_HVAC
    }

    namespace GWM {
        class Behavioral_Model_GWM
        class RemotiveBroker_GWM
    }

    namespace TCU {
        class Behavioral_Model_TCU
        class RemotiveBroker_TCU
    }

    namespace IHU {
        class Behavioral_Model_IHU
        class RemotiveBroker_IHU
    }

    class ChassisCan {
        <<CAN>>
    }

    class BodyCan {
        <<CAN>>
    }

    class DriverCan {
        <<CAN>>
    }


    class SOMEIP {
        <<SOMEIP>>
    }


    class TopologyBroker
    class Android
    class TestSuite
    class Webapp
    class Behave

    RemotiveBroker_ABS -- ChassisCan
    RemotiveBroker_GWM -- ChassisCan

    RemotiveBroker_GWM -- BodyCan
    RemotiveBroker_TCU -- BodyCan
    RemotiveBroker_HVAC -- BodyCan

    RemotiveBroker_BCM -- BodyCan
    RemotiveBroker_BCM -- DriverCan


    RemotiveBroker_IHU -- SOMEIP
    RemotiveBroker_GWM -- SOMEIP


    Behavioral_Model_ABS -- RemotiveBroker_ABS
    Behavioral_Model_BCM -- RemotiveBroker_BCM
    Behavioral_Model_GWM -- RemotiveBroker_GWM
    Behavioral_Model_TCU -- RemotiveBroker_TCU
    Behavioral_Model_IHU -- RemotiveBroker_IHU
    Android -- Behavioral_Model_IHU

    TestSuite ..> TopologyBroker
    Behave ..> TopologyBroker
    Webapp ..> TopologyBroker

    TopologyBroker .. RemotiveBroker_ABS
    TopologyBroker .. RemotiveBroker_BCM
    TopologyBroker .. RemotiveBroker_GWM
    TopologyBroker .. RemotiveBroker_HVAC
    TopologyBroker .. RemotiveBroker_IHU
    TopologyBroker .. RemotiveBroker_TCU
```

Where we can see that the IHU is connected to the android emulator.

### Platform reference

[../../platform/remotive-car.platform.yaml](../../platform/remotive-car.platform.yaml) describes the platform to which all instances refer. In this android instance only blue parts are partcipants [main.instance.yaml](main.instance.yaml).

```mermaid
---
config:
  class:
    hideEmptyMembersBox: true
---
    classDiagram

    class DEVS2 {
    }
    class DEVS2:::supress

    class RL {
    }
    class RL:::supress

    class RLCM {
    }
    class RLCM:::supress

    class DIM {
    }
    class DIM:::supress

    class FLCM {
    }
    class FLCM:::supress

    class HVAC {
    }

    class TCU {
    }

    class SCCM {
    }
    class SCCM:::supress

    class BCM {
    }

    class PAM {
    }
    class PAM:::supress

    class GWM {
    }

    class ABS {
    }

    class IHU {
    }

    class BodyCan {
        <<CAN>>
    }

    class DriverCan {
        <<CAN>>
    }

    class ChassisCan {
        <<CAN>>
    }

    class SOMEIP {
        <<SOMEIP>>
    }

    class RearLightLIN {
        <<LIN>>
    }
    class RearLightLIN:::supress

    DEVS2 -- RearLightLIN

    RL -- RearLightLIN

    RLCM -- RearLightLIN
    RLCM -- BodyCan

    ABS -- ChassisCan

    DIM -- BodyCan

    FLCM -- BodyCan

    PAM -- BodyCan

    HVAC -- BodyCan

    BCM -- BodyCan
    BCM -- DriverCan

    GWM -- BodyCan
    GWM -- ChassisCan
    GWM -- SOMEIP

    IHU -- SOMEIP

    SCCM -- DriverCan

    TCU -- DriverCan

    classDef supress fill:#ffffffff
```

## Host setup

You will need the following tools

- `RemotiveCLI` <https://developer.remotivelabs.com/docs/remotive-cli/installation>
- `RemotiveTopology` <https://developer.remotivelabs.com/docs/remotive-topology/install>
- On Linux, this example requires that you run `RemotiveBus` service on your machine to enable CAN and VLAN networks in Docker, see installation instructions [here](https://developer.remotivelabs.com/docs/remotive-bus/install). Alternatively include [can_over_udp.instance.yaml](../../settings/can_over_udp.settings.instance.yaml) and [vlan_using_bridge.settings.instance.yaml](../../settings/vlan_using_bridge.settings.instance.yaml) in your instance, as shown in the examples below.
- `git lfs` <https://git-lfs.com/> make sure to do `git lfs pull` if `git lfs` wasn't installed during `git clone`. For Ubuntu `sudo apt install git-lfs`.
- (Optional) `socat` [See Emulator on host](EMULATOR_ON_HOST.md)
- (Optional) `Android-Studio` [See Emulator on host](EMULATOR_ON_HOST.md)

## Getting started

The example can be run either using an Android emulator or a Cuttlefish instance. The emulator can be run either on the host machine or within docker and the Cuttlefish instance can be run within the docker environment. Cuttlefish comes in two variants: [cuttlefish.instance.yaml](cuttlefish.instance.yaml) uses an Android 16 image with built-in SOME/IP support where the Cuttlefish container is the IHU ECU, and [cuttlefish_vhal_grpc.instance.yaml](cuttlefish_vhal_grpc.instance.yaml) uses an Android 15 image where the IHU behavioral model bridges SOME/IP to Cuttlefish over VHAL gRPC, which needs no changes to the Android build. The easiest way to get started is by running the emulator within docker as it requires far less setup. For running the emulator on the host the instructions will differ based on your platform.

> :warning: When running Cuttlefish or the emulator within Docker it requires hardware virtualization using KVM to achieve any reasonable performance. This means that running the example in this configuration is limited to Linux only using x86_64 architecture.

#### Configuration

All configuration is done using RemotiveTopology instance files:

> :link: [Main instance](main.instance.yaml)<br>
> :link: [CAN over UDP](../../settings/can_over_udp.settings.instance.yaml)<br>
> :link: [VLAN using bridge](../../settings/vlan_using_bridge.settings.instance.yaml)<br>

Notice how the main instance includes other instance configuration files and also the platform configuration. RemotiveTopology is based around a modular approach to describe both platforms and different ways to instantiate them. Every ECU is one file from [instances/ecus](../ecus/README.md). The IHU has one file per way of attaching Android to it: [IHU/android_emulator.instance.yaml](../ecus/IHU/android_emulator.instance.yaml) for an emulator, [IHU/vhal_grpc.instance.yaml](../ecus/IHU/vhal_grpc.instance.yaml) for a separate Cuttlefish container over VHAL gRPC and [IHU/cuttlefish.instance.yaml](../ecus/IHU/cuttlefish.instance.yaml) for Cuttlefish as the IHU container itself. The files next to this one pick one of them and add what it needs.

#### Optional: instrument cluster

The same modularity makes the [instrument cluster](../agl_cluster/README.md) an option for this instance. Adding
[DIM/agl_cluster.instance.yaml](../ecus/DIM/agl_cluster.instance.yaml) to the build replaces the DIM broker with
the cluster container, which then shows the recorded drive next to Android:

```bash
remotive topology build \
-f remotive_car/instances/android/main.instance.yaml \
-f remotive_car/instances/android/cuttlefish.instance.yaml \
-f remotive_car/instances/ecus/DIM/agl_cluster.instance.yaml \
remotive_car/build
```

Run the instance as usual. The cluster is served at <http://localhost:6080> and
can be embedded in the 3D car, see the [cluster README](../agl_cluster/README.md#cluster-in-the-3d-car). The cluster
reads the CAN buses over SocketCAN, so it needs RemotiveBus on the host.

### Use cases

[Cuttlefish](../../../usecases/ANDROID_CUTTLEFISH.md)
[Emulator](../../../usecases/ANDROID_EMULATOR.md)

### Troubleshoot

This guide presents deployment on various operating systems, but Linux is the preferred host operating system.
- Playback is not operational: Make sure you have `git lfs` installed, [see Host setup](#host-setup).
