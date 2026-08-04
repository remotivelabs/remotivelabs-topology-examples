# Behavioral models in python

Writing behavioral models in python is a very simple way of creating models for ECUs that don't yet exist. For more complex models it is also useful to create unit tests.

- Part of the [RemotiveCar example](../remotive_car/DOCS.md) 
- Behavioral models: [bcm](../remotive_car/models/bcm/python/bcm) and [gwm](../remotive_car/models/gwm/python/gwm)
- Unit tests: [tests](../remotive_car/models/bcm/python/tests)
- Instance files: [bcm](../remotive_car/models/bcm.bm.instance.yaml) and [gwm](../remotive_car/models/gwm.bm.instance.yaml)

Notice:
- The platform is included in each instance, since the instance depends on the platform. However, in a larger platform it would probably make sense to only include the part of the platform describing each ECU.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.

## Running unit tests

Complex behavioral models should have unit tests. To run the unit tests for BCM:

```bash
cd remotive_car/models/bcm/python/bcm
uv sync
uv run poe test
```
