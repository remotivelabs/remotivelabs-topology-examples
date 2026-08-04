# Test cases in python (behave)

Using behave to write test cases allows your domain experts to more easily understand the tests that are being run.

- Part of the [RemotiveCar example](../remotive_car/DOCS.md) 
- Example features: [blink_left.feature](../remotive_car/tests/behave/features/blink_left.feature) and [hazard_light.feature](../remotive_car/tests/behave/features/hazard_light.feature)
- Example step implementation [example_steps.py](../remotive_car/tests/behave/features/steps/example_steps.py)
- Control how to run tests: [behave.instance.yaml](../remotive_car/tests/behave.instance.yaml)
- Python project: [pyproject.toml](../remotive_car/tests/pyproject.toml)

Start topology and run tests:

```bash
remotive topology build ...
docker compose -f ... --profile behave up --abort-on-container-exit
```

Optionally first start topology and then run tests (useful when writing tests)

```bash
# build and start
remotive topology build ...
docker compose -f ... up
# run tests in separate shell (dont forget --build)
docker compose -f ... up behave --build
```

Example with `hello_world` instance:

```bash
remotive topology build -f remotive_car/instances/hello_world/main.instance.yaml remotive_car/build
docker compose -f remotive_car/build/remotive_car_hello_world/docker-compose.yml --profile behave up --abort-on-container-exit --build
```

Notice:
- Tests are run in a container as part of the topology.
- By using a profile you can use the same instance and use the profile to control if the tests should run or not.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.
