from __future__ import annotations

import os

import pytest


# pytest_addoption hook
def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--broker_url",
        action="store",
        default=os.environ.get("BROKER_URL", "http://127.0.0.1:50051"),
        type=str,
        help="Broker to run tests towards, e.g. http://127.0.0.1:50051.",
    )
    parser.addoption(
        "--android_device_host",
        action="store",
        default=os.environ.get("ANDROID_DEVICE_HOST", "localhost"),
        type=str,
        help="Host where the android device residies",
    )
