# Test cases in python (pytest)

Using pytest to write test cases is a simple way to express your test cases as code.

- Part of the [RemotiveCar example](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/DOCS.md)
- Example test case: [test_simulate_driver.py](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/pytest/test_simulate_driver.py)
- Control how to run tests: [pytest.instance.yaml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/pytest.instance.yaml)
- Python project: [pyproject.toml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/tests/pyproject.toml)

The commands on this page run in a clone of the [RemotiveCar repository](https://github.com/remotivelabs/remotivelabs-remotive-car):

```bash
git clone https://github.com/remotivelabs/remotivelabs-remotive-car.git
cd remotivelabs-remotive-car
```

Start topology and run tests:

```bash
remotive topology build ...
docker compose -f ... --profile tester up --abort-on-container-exit
```

Optionally first start topology and then run tests (useful when writing tests)

```bash
# build and start
remotive topology build ...
docker compose -f ... up
# run tests in separate shell (dont forget --build)
docker compose -f ... up tester --build
```

Example with `hello_world` instance:

```bash
remotive topology build -f instances/hello_world/main.instance.yaml build
docker compose -f build/remotive_car_hello_world/docker-compose.yml --profile tester up --abort-on-container-exit --build
```

Notice:
- Tests are run in a container as part of the topology.
- By using a profile you can use the same instance and use the profile to control if the tests should run or not.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.
