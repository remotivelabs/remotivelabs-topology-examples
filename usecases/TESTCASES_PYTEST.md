# Test cases in python (pytest)

Using pytest to write test cases is a simple way to express your test cases as code.

- Part of the [RemotiveCar example](../remotive_car/DOCS.md) 
- Example test case: [test_simulate_driver.py](../remotive_car/tests/pytest/test_simulate_driver.py)
- Control how to run tests: [pytest.instance.yaml](../remotive_car/tests/pytest.instance.yaml)
- Python project: [pyproject.toml](../remotive_car/tests/pyproject.toml)

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
remotive topology build -f remotive_car/instances/hello_world/main.instance.yaml remotive_car/build
docker compose -f remotive_car/build/remotive_car_hello_world/docker-compose.yml --profile tester up --abort-on-container-exit --build
```

Notice:
- Tests are run in a container as part of the topology.
- By using a profile you can use the same instance and use the profile to control if the tests should run or not.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.
