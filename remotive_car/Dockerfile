FROM python:3.13-slim AS base

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv==0.9.2

CMD ["placeholder_override", "--allow-root"]

FROM base AS jupyter

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=common/jupyter/uv.lock,target=uv.lock \
    --mount=type=bind,source=common/jupyter/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev

ENV PATH="/.venv/bin:$PATH"
RUN jupyter labextension enable --py widgetsnbextension

CMD ["jupyter-lab", "--allow-root", "--ip", "0.0.0.0", "--port", "8888", "--NotebookApp.token=remotivelabs", "--no-browser", "--FileCheckpoints.checkpoint_dir=/tmp"]

FROM base AS tester

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=tests/uv.lock,target=uv.lock \
    --mount=type=bind,source=tests/pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-dev
ENV PATH="/.venv/bin:$PATH"

CMD ["pytest", "--broker_url=http://topology-broker.com:50051", "-s", "-vv"]


FROM base AS model
ARG MODEL_PATH

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=models/${MODEL_PATH}/uv.lock,target=/uv.lock,readonly \
    --mount=type=bind,source=models/${MODEL_PATH}/pyproject.toml,target=/pyproject.toml,readonly \
    uv sync --locked --no-install-project --no-dev

COPY models/${MODEL_PATH}/ .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PATH="/.venv/bin:$PATH"

CMD ["placeholder_override", "--allow-root"]

FROM model AS ihu_android
RUN apt update && apt install -y android-tools-adb socat

# prepare the environment variable for the Android emulator authentication and ADB connection
ENTRYPOINT ["/bin/sh", "-c", \
    # Save optional emulator auth token
    "echo \"$ANDROID_EMULATOR_AUTH\" > ~/.emulator_console_auth_token && \
    # Redirect emulator console port to 6000 proxy (5554 does not accept remote connections)
    socat TCP-LISTEN:5554,fork,reuseaddr TCP:$ANDROID_EMULATOR_ADDRESS:6000 & \
    # Redirect emulator hard-coded properties port from localhost to emulator host
    socat TCP-LISTEN:33452,fork,reuseaddr TCP:$ANDROID_EMULATOR_ADDRESS:33452 & \
    # Wait for emulator to be ready before starting application
    until adb shell getprop sys.boot_completed 2>/dev/null | grep -q \"1\"; do echo \"Waiting for android emulator to be ready...\"; sleep 5; done && \
    # Run application
    exec \"$@\"", "--"]
# ENTRYPOINT ["/bin/sh", "-c", "echo \"$ANDROID_EMULATOR_AUTH\" > ~/.emulator_console_auth_token & exec \"$@\"", "--"]
