# Test cases in python (behave)

Using behave to write test cases allows your domain experts to more easily understand the tests that are being run.

- Part of the [RemotiveCar example](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/DOCS.md)
- Example features: [blink_left.feature](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/behave/features/blink_left.feature) and [hazard_light.feature](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/behave/features/hazard_light.feature)
- Example step implementation [example_steps.py](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/behave/features/steps/example_steps.py)
- Control how to run tests: [behave.instance.yaml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/behave.instance.yaml)
- Python project: [pyproject.toml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/pyproject.toml)

The commands on this page run in a clone of the [RemotiveCar repository](https://github.com/remotivelabs/remotivelabs-remotive-car):

```bash
git clone https://github.com/remotivelabs/remotivelabs-remotive-car.git
cd remotivelabs-remotive-car
```

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
remotive topology build -f instances/hello_world/main.instance.yaml build
docker compose -f build/remotive_car_hello_world/docker-compose.yml --profile behave up --abort-on-container-exit --build
```

Notice:
- Tests are run in a container as part of the topology.
- By using a profile you can use the same instance and use the profile to control if the tests should run or not.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.
