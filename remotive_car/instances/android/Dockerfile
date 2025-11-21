FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv==0.9.2

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=/uv.lock,readonly \
    --mount=type=bind,source=pyproject.toml,target=/pyproject.toml,readonly \
    uv sync --locked --no-install-project --no-dev

COPY pyproject.toml .
COPY uv.lock .
COPY playback/ playback/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

ENV PATH="/.venv/bin:$PATH"

CMD ["placeholder_override", "--allow-root"]
