# RemotiveLabs Topology Examples

Easy to get going examples:

- [Getting started](./getting_started/README.md)
- [Lighting and Steering - larger example](./lighting_and_steering/README.md)

More detailed examples:

- [E2E RestBus](./e2e_restbus/README.md)
- [Jupyter examples](./jupyter_demo/README.md)
- [SOME/IP](./some_ip/README.md)

## Documentation

- [RemotiveLabs RemotiveTopology framework documentation](https://docs.remotivelabs.com/apis/python/remotivelabs/topology)
- [RemotiveLabs documentation home](https://docs.remotivelabs.com/)

## RemotiveBroker License (prerequisite)

The examples assume that you have a [env file](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/#use-the-env_file-attribute) with a [RemotiveBroker](https://docs.remotivelabs.com/docs/remotive-broker) license in the root of this repository called `REMOTIVEBROKER_LICENSE`. Alternatively you can `export REMOTIVEBROKER_LICENSE` to a custom path. The env file should set the variable `LICENSE`:
```bash
LICENSE="<YOUR LICENSE>"
```
