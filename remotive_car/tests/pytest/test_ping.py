from typing import AsyncIterator

import pytest_asyncio
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import PingRequest
from remotivelabs.topology.control.client import ControlClient

import pytest


@pytest_asyncio.fixture()
async def broker_url(request: pytest.FixtureRequest) -> AsyncIterator[str]:
    yield request.config.getoption("broker_url")


@pytest.mark.parametrize("ecu", ["SCCM", "BCM", "GWM", "IHU"])
@pytest.mark.asyncio
async def test_ping_topology(broker_url: str, ecu: str):
    async with (
        BrokerClient(broker_url) as broker_client,
        ControlClient(broker_client) as cc,
    ):
        await cc.send(target_ecu=ecu, request=PingRequest(), timeout=1, retries=10)
