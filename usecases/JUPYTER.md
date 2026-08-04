# Jupyter notebook

Using RemotiveTopology framework from Jupyter notebook allows you to interact with a running instance and easily create custom user interfaces.

- Part of the [RemotiveCar example](../remotive_car/DOCS.md) 
- Example notebook [car.ipynb](../remotive_car/common/jupyter/car.ipynb)
- Control how to run [jupyter.instance.yaml](../remotive_car/common/jupyter/jupyter.instance.yaml)
- Python project: [pyproject.toml](../remotive_car/common/jupyter/pyproject.toml)

Start topology and jupyter:

```bash
remotive topology build ...
docker compose -f ... --profile jupyter up
```

Example with `hello_world` instance:

```bash
remotive topology build -f remotive_car/instances/hello_world/main.instance.yaml remotive_car/build
docker compose -f remotive_car/build/remotive_car_hello_world/docker-compose.yml --profile jupyter up --build
```

Notice:
- Jupyter is run in a container as part of the topology.
- By using a profile you can use the same instance and use the profile to control if Jupyter should run or not.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.
