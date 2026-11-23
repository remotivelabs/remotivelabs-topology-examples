# RemotiveLabs Topology Examples
This repository contains example topologies showcasing how to set up and run RemotiveLabs tools.
It includes minimal examples for getting started quickly, as well as examples of specific features.

> **RemotiveCar has moved.** The larger RemotiveCar example now lives in its own repository,
> [remotivelabs-remotive-car](https://github.com/remotivelabs/remotivelabs-remotive-car). The history of this repository was reset when it moved, which made it much
> smaller to clone. If you cloned this repository before, clone it again, or run `git fetch && git reset --hard origin/main`.

## Quick Start
Get up and running with a minimal example:

- [Getting Started](./getting_started/README.md)
- [Basic restbus](./basic_restbus/README.md)
- [Quickstart template](https://github.com/remotivelabs/remotivelabs-topology-quickstart) - the finished project of the [Your first topology](https://developer.remotivelabs.com/docs/get-started/first-topology) tutorial, ready to use as a template for your own project

## More Examples

- [Ethernet peer-to-peer](./ethernet_p2p/README.md) - Validate ECUs that communicate over Ethernet, from behavioral model to hardware
- [Tesla](./tesla/README.md) - Play back a recording from a Tesla Model 3, including camera videos
- [EdgeShark for Podman](./edgeshark_for_podman/README.md) - A docker compose file for EdgeShark that works with Podman

## Use Cases
Understand what you can do with RemotiveTopology by exploring [various use cases](./USECASES.md).

## Documentation

- [RemotiveTopology documentation](https://developer.remotivelabs.com/docs/remotive-topology)
- [RemotiveLabs RemotiveTopology framework documentation](https://developer.remotivelabs.com/apis/python/remotivelabs/topology) (python API)
- [RemotiveLabs documentation home](https://developer.remotivelabs.com/)

## Prerequisites

To run these examples, you'll need:
- A valid RemotiveTopology subscription (free trial available)
- RemotiveCLI installed

**New to RemotiveTopology?** Get started with our [installation guide](https://developer.remotivelabs.com/docs/remotive-topology) to create your free trial subscription. You can also [book a meeting](https://meetings-eu1.hubspot.com/per-sigurdson/remotivelabs-platform-intro?uuid=16d16894-7cf9-471a-8ed8-7481ba152fc3) if you want a hands-on demo.

## License

The example code in this repository is licensed under the [MIT License](./LICENSE), so you are free to copy, modify and reuse it in your own projects.

Running the examples, however, requires a RemotiveLabs account. The RemotiveLabs software the examples depend on (such as RemotiveBroker, RemotiveTopology and RemotiveCLI) is not covered by the MIT License; it is provided under the RemotiveLabs Terms of Use at https://www.remotivelabs.com/license.

Some examples include third-party files that keep their original licenses, as noted in those files.

## Support

Contact support@remotivelabs.com if you have any problems or questions!
