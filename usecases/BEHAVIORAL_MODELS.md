# Behavioral models in python

Writing behavioral models in python is a very simple way of creating models for ECUs that don't yet exist. For more complex models it is also useful to create unit tests.

- Part of the [RemotiveCar example](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/DOCS.md)
- Behavioral models: [bcm](https://github.com/remotivelabs/remotivelabs-remotive-car/tree/main/models/bcm/python/bcm) and [gwm](https://github.com/remotivelabs/remotivelabs-remotive-car/tree/main/models/gwm/python/gwm)
- Unit tests: [tests](https://github.com/remotivelabs/remotivelabs-remotive-car/tree/main/models/bcm/python/tests)
- Instance files: [BCM/python](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/instances/ecus/BCM/python.instance.yaml) and [GWM/python](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/instances/ecus/GWM/python.instance.yaml)

The commands on this page run in a clone of the [RemotiveCar repository](https://github.com/remotivelabs/remotivelabs-remotive-car):

```bash
git clone https://github.com/remotivelabs/remotivelabs-remotive-car.git
cd remotivelabs-remotive-car
```

Notice:
- The platform is included in each instance, since the instance depends on the platform. However, in a larger platform it would probably make sense to only include the part of the platform describing each ECU.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.

## Running unit tests

Complex behavioral models should have unit tests. To run the unit tests for BCM:

```bash
cd models/bcm/python/bcm
uv sync
uv run poe test
```
