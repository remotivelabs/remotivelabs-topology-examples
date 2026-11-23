# Jupyter notebook

Using RemotiveTopology framework from Jupyter notebook allows you to interact with a running instance and easily create custom user interfaces.

- Part of the [RemotiveCar example](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/DOCS.md)
- Example notebook [car.ipynb](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/common/jupyter/car.ipynb)
- Control how to run [jupyter.instance.yaml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/common/jupyter/jupyter.instance.yaml)
- Python project: [pyproject.toml](https://github.com/remotivelabs/remotivelabs-remotive-car/blob/main/common/jupyter/pyproject.toml)

The commands on this page run in a clone of the [RemotiveCar repository](https://github.com/remotivelabs/remotivelabs-remotive-car):

```bash
git clone https://github.com/remotivelabs/remotivelabs-remotive-car.git
cd remotivelabs-remotive-car
```

Start topology and jupyter:

```bash
remotive topology build ...
docker compose -f ... --profile jupyter up
```

Example with `hello_world` instance:

```bash
remotive topology build -f instances/hello_world/main.instance.yaml build
docker compose -f build/remotive_car_hello_world/docker-compose.yml --profile jupyter up --build
```

Notice:
- Jupyter is run in a container as part of the topology.
- By using a profile you can use the same instance and use the profile to control if Jupyter should run or not.
- In this example the same Dockerfile is used for all python code in order to reuse the same base image. You can of course use separate Dockerfile for each container.
